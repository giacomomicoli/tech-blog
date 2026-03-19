"""Background task that polls Notion for content changes and invalidates stale cache."""

import asyncio
import logging

from src.cache import cache_invalidate
from src.config import settings
from src.notion.client import notion_client

logger = logging.getLogger(__name__)


async def sync_loop():
    """Periodically check for recently edited posts and bust their cache."""
    interval = settings.sync_interval_minutes * 60
    logger.info("Sync loop started (interval: %ds)", interval)

    # Track last_edited_time per page ID
    known_edits: dict[str, str] = {}

    while True:
        await asyncio.sleep(interval)
        try:
            await _check_for_updates(known_edits)
        except Exception:
            logger.exception("Sync loop error")


async def _check_for_updates(known_edits: dict[str, str]):
    """Query recent edits and invalidate changed posts."""
    sorts = [{"timestamp": "last_edited_time", "direction": "descending"}]
    count = 0

    async for page in notion_client.query_database(sorts=sorts):
        count += 1
        if count > 20:
            break

        page_id = page.get("id", "")
        last_edited = page.get("last_edited_time", "")
        props = page.get("properties", {})

        # Extract slug for targeted invalidation
        slug_prop = props.get("Slug", {})
        slug_items = slug_prop.get("rich_text", [])
        slug = "".join(item.get("plain_text", "") for item in slug_items) if slug_items else ""

        prev = known_edits.get(page_id)
        known_edits[page_id] = last_edited

        if prev is not None and prev != last_edited:
            logger.info("Post changed: %s (slug=%s)", page_id, slug)
            if slug:
                # Invalidate this post in all languages
                await cache_invalidate(f"blog:*:posts:{slug}")
            # Also invalidate listing, hero, and top caches for all languages
            await cache_invalidate("blog:*:posts:*")
            await cache_invalidate("blog:*:hero")
            await cache_invalidate("blog:*:top")
