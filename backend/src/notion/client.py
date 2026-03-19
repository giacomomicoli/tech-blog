import asyncio
import logging
import time
from collections.abc import AsyncGenerator
from typing import Any

import httpx

from src.config import settings

logger = logging.getLogger(__name__)

_TWITTER_HOSTS = {"twitter.com", "x.com", "www.twitter.com", "www.x.com"}
_OEMBED_URL = "https://publish.twitter.com/oembed"


class NotionAPIError(Exception):
    def __init__(self, status: int, code: str, message: str):
        self.status = status
        self.code = code
        super().__init__(f"Notion API {status} ({code}): {message}")


class NotionRateLimited(NotionAPIError):
    pass


class NotionNotFound(NotionAPIError):
    pass


class NotionUnauthorized(NotionAPIError):
    pass


class _RateLimiter:
    """Token-bucket rate limiter: avg 3 requests/second."""

    def __init__(self, rate: float = 3.0):
        self._rate = rate
        self._min_interval = 1.0 / rate
        self._last_request = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            now = time.monotonic()
            wait = self._min_interval - (now - self._last_request)
            if wait > 0:
                await asyncio.sleep(wait)
            self._last_request = time.monotonic()


class NotionClient:
    BASE_URL = "https://api.notion.com/v1"
    MAX_RETRIES = 3

    def __init__(
        self,
        api_key: str | None = None,
        api_version: str | None = None,
    ):
        self._api_key = api_key or settings.notion_api_key
        self._api_version = api_version or settings.notion_api_version
        self._rate_limiter = _RateLimiter()
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Notion-Version": self._api_version,
                    "Content-Type": "application/json",
                },
                timeout=30.0,
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def _request(
        self,
        method: str,
        path: str,
        json: dict | None = None,
        params: dict | None = None,
    ) -> dict:
        client = await self._get_client()

        for attempt in range(self.MAX_RETRIES):
            await self._rate_limiter.acquire()
            response = await client.request(method, path, json=json, params=params)

            if response.status_code == 200:
                return response.json()

            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 1))
                if attempt < self.MAX_RETRIES - 1:
                    await asyncio.sleep(retry_after * (2**attempt))
                    continue
                body = response.json()
                raise NotionRateLimited(
                    429, body.get("code", "rate_limited"), body.get("message", "")
                )

            body = response.json()
            code = body.get("code", "unknown")
            message = body.get("message", "Unknown error")

            if response.status_code == 401:
                raise NotionUnauthorized(401, code, message)
            if response.status_code == 404:
                raise NotionNotFound(404, code, message)
            raise NotionAPIError(response.status_code, code, message)

        # Should not reach here, but just in case
        raise NotionAPIError(0, "max_retries", "Max retries exceeded")

    async def _paginate(
        self,
        method: str,
        path: str,
        body: dict | None = None,
        params: dict | None = None,
        page_size: int = 100,
    ) -> AsyncGenerator[dict, None]:
        """Yield all results across paginated responses."""
        start_cursor: str | None = None

        while True:
            if method == "POST":
                payload = {**(body or {}), "page_size": page_size}
                if start_cursor:
                    payload["start_cursor"] = start_cursor
                data = await self._request(method, path, json=payload)
            else:
                p = {**(params or {}), "page_size": str(page_size)}
                if start_cursor:
                    p["start_cursor"] = start_cursor
                data = await self._request(method, path, params=p)

            for item in data.get("results", []):
                yield item

            if not data.get("has_more"):
                break
            start_cursor = data.get("next_cursor")

    # ── Public API ──────────────────────────────────────────────

    async def query_database(
        self,
        data_source_id: str | None = None,
        filter: dict | None = None,
        sorts: list[dict] | None = None,
    ) -> AsyncGenerator[dict, None]:
        """Query a Notion data source (database). Yields page objects.

        API version 2025-09-03 uses /v1/data_sources/{id}/query instead of
        the old /v1/databases/{id}/query endpoint.
        """
        ds_id = data_source_id or settings.notion_data_source_id
        body: dict[str, Any] = {}
        if filter:
            body["filter"] = filter
        if sorts:
            body["sorts"] = sorts

        async for page in self._paginate("POST", f"/data_sources/{ds_id}/query", body=body):
            yield page

    async def get_page(self, page_id: str) -> dict:
        """Retrieve a single page by ID."""
        return await self._request("GET", f"/pages/{page_id}")

    async def get_blocks(self, block_id: str) -> list[dict]:
        """Retrieve all blocks for a page/block, recursively fetching children."""
        blocks: list[dict] = []

        async for block in self._paginate("GET", f"/blocks/{block_id}/children"):
            if block.get("has_children"):
                block["children"] = await self.get_blocks(block["id"])
            blocks.append(block)

        await self.enrich_embed_blocks(blocks)
        return blocks

    async def enrich_embed_blocks(self, blocks: list[dict]) -> None:
        """Walk blocks in-place and resolve Twitter/X embed URLs via oEmbed.

        For each embed block whose URL is a Twitter or X post, fetches the
        oEmbed HTML from publish.twitter.com and stores it as ``oembed_html``
        inside the block's ``embed`` dict.  Non-Twitter embeds are left
        untouched.  Children are processed recursively.
        """
        tasks = []
        for block in blocks:
            btype = block.get("type")
            if btype == "embed":
                url = block.get("embed", {}).get("url", "")
                try:
                    host = httpx.URL(url).host.lstrip("www.")
                except Exception:
                    host = ""
                if host in _TWITTER_HOSTS:
                    tasks.append(self._fetch_twitter_oembed(block, url))
            # Recurse into already-fetched children
            children = block.get("children")
            if children:
                tasks.append(self.enrich_embed_blocks(children))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _fetch_twitter_oembed(self, block: dict, url: str) -> None:
        """Fetch oEmbed HTML for a tweet URL and inject it into the block."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    _OEMBED_URL,
                    params={"url": url, "omit_script": "true", "dnt": "true"},
                )
            if response.status_code == 200:
                data = response.json()
                block["embed"]["oembed_html"] = data.get("html", "")
            else:
                logger.warning("oEmbed fetch returned %s for %s", response.status_code, url)
        except Exception as exc:
            logger.warning("oEmbed fetch failed for %s: %s", url, exc)

    async def search(
        self,
        query: str | None = None,
        filter: dict | None = None,
    ) -> AsyncGenerator[dict, None]:
        """Search across pages and databases shared with integration."""
        body: dict[str, Any] = {}
        if query:
            body["query"] = query
        if filter:
            body["filter"] = filter

        async for item in self._paginate("POST", "/search", body=body):
            yield item


# Module-level singleton
notion_client = NotionClient()
