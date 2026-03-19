"""Blog post API endpoints."""

from fastapi import APIRouter, HTTPException, Query

from src.cache import (
    cache_get,
    cache_set,
    categories_key,
    hero_key,
    page_key,
    post_key,
    posts_list_key,
    tags_key,
    top_key,
)
from src.config import settings
from src.notion.client import NotionAPIError, NotionNotFound, notion_client
from src.notion.renderer import extract_toc, render_blocks

router = APIRouter(prefix="/api")


def _validate_lang(lang: str) -> str:
    """Validate and return the language code, falling back to default."""
    if lang in settings.parsed_locales:
        return lang
    return settings.default_locale


# ── Property extraction helpers ─────────────────────────────


def _get_plain_text(prop: dict) -> str:
    """Extract plain text from a title or rich_text property."""
    ptype = prop.get("type", "")
    items = prop.get(ptype, [])
    if isinstance(items, list):
        return "".join(item.get("plain_text", "") for item in items)
    return ""


def _get_select(prop: dict) -> str | None:
    sel = prop.get("select")
    return sel.get("name") if sel else None


def _get_multi_select(prop: dict) -> list[str]:
    return [opt.get("name", "") for opt in prop.get("multi_select", [])]


def _get_date(prop: dict) -> str | None:
    d = prop.get("date")
    return d.get("start") if d else None


def _get_checkbox(prop: dict) -> bool:
    return prop.get("checkbox", False)


def _get_number(prop: dict) -> int | None:
    val = prop.get("number")
    return int(val) if val is not None else None


def _get_relation_ids(prop: dict) -> list[str]:
    return [rel.get("id", "") for rel in prop.get("relation", []) if rel.get("id")]


def _get_url(prop: dict) -> str | None:
    return prop.get("url")


def _extract_post_meta(page: dict) -> dict:
    """Extract blog post metadata from a Notion page object."""
    props = page.get("properties", {})
    title = _get_plain_text(props.get("Name", {}))
    slug = _get_plain_text(props.get("Slug", {}))
    excerpt = _get_plain_text(props.get("Excerpt", {}))

    return {
        "id": page.get("id", ""),
        "slug": slug,
        "title": title,
        "excerpt": excerpt,
        "category": _get_select(props.get("Category", {})),
        "tags": _get_multi_select(props.get("Tags", {})),
        "published_date": _get_date(props.get("Published Date", {})),
        "cover_image": _get_url(props.get("Cover", {})),
        "author": _get_plain_text(props.get("Author", {})),
        "featured": _get_checkbox(props.get("Featured", {})),
        "language": _get_select(props.get("Language", {})) or settings.default_locale,
        "hero_position": _get_number(props.get("Hero Position", {})),
        "top": _get_checkbox(props.get("Top", {})),
        "related_post_ids": _get_relation_ids(props.get("Related Posts", {})),
    }


def _estimate_reading_time(blocks: list[dict]) -> int:
    """Estimate reading time in minutes from blocks (~200 words/min)."""

    def count_words(blocks_list: list[dict]) -> int:
        total = 0
        for block in blocks_list:
            btype = block.get("type", "")
            data = block.get(btype, {})
            rich_text = data.get("rich_text", [])
            if isinstance(rich_text, list):
                text = " ".join(item.get("plain_text", "") for item in rich_text)
                total += len(text.split())
            children = block.get("children", [])
            if children:
                total += count_words(children)
        return total

    words = count_words(blocks)
    return max(1, round(words / 200))


# ── Endpoints ───────────────────────────────────────────────


@router.get("/posts")
async def list_posts(
    tag: str | None = Query(None),
    category: str | None = Query(None),
    featured: bool | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    lang: str = Query(""),
):
    """List published blog posts with optional filtering."""
    lang = _validate_lang(lang)
    cache_k = posts_list_key(lang=lang, tag=tag, category=category, featured=featured, page=page)
    cached = await cache_get(cache_k)
    if cached:
        return cached

    # Build filter: Published = true, Language = lang
    conditions: list[dict] = [
        {"property": "Published", "checkbox": {"equals": True}},
        {"property": "Language", "select": {"equals": lang}},
    ]
    if tag:
        conditions.append(
            {"property": "Tags", "multi_select": {"contains": tag}},
        )
    if category:
        conditions.append(
            {"property": "Category", "select": {"equals": category}},
        )
    if featured is not None:
        conditions.append(
            {"property": "Featured", "checkbox": {"equals": featured}},
        )

    db_filter = {"and": conditions} if len(conditions) > 1 else conditions[0]
    sorts = [{"property": "Published Date", "direction": "descending"}]

    all_posts: list[dict] = []
    async for page_obj in notion_client.query_database(filter=db_filter, sorts=sorts):
        meta = _extract_post_meta(page_obj)
        del meta["related_post_ids"]
        all_posts.append(meta)

    total = len(all_posts)
    start = (page - 1) * limit
    end = start + limit
    paginated = all_posts[start:end]

    result = {
        "posts": paginated,
        "total": total,
        "page": page,
        "has_more": end < total,
    }
    await cache_set(cache_k, result)
    return result


@router.get("/posts/hero")
async def hero_posts(lang: str = Query("")):
    """Return up to 5 posts with hero_position 1-5, sorted by position."""
    lang = _validate_lang(lang)
    cache_k = hero_key(lang)
    cached = await cache_get(cache_k)
    if cached:
        return cached

    db_filter = {
        "and": [
            {"property": "Published", "checkbox": {"equals": True}},
            {"property": "Language", "select": {"equals": lang}},
            {"property": "Hero Position", "number": {"is_not_empty": True}},
        ]
    }
    sorts = [{"property": "Hero Position", "direction": "ascending"}]

    posts: list[dict] = []
    async for page_obj in notion_client.query_database(filter=db_filter, sorts=sorts):
        meta = _extract_post_meta(page_obj)
        del meta["related_post_ids"]
        posts.append(meta)
        if len(posts) >= 5:
            break

    await cache_set(cache_k, posts)
    return posts


@router.get("/posts/top")
async def top_posts(lang: str = Query("")):
    """Return up to 3 posts flagged as Top, sorted by date descending."""
    lang = _validate_lang(lang)
    cache_k = top_key(lang)
    cached = await cache_get(cache_k)
    if cached:
        return cached

    db_filter = {
        "and": [
            {"property": "Published", "checkbox": {"equals": True}},
            {"property": "Language", "select": {"equals": lang}},
            {"property": "Top", "checkbox": {"equals": True}},
        ]
    }
    sorts = [{"property": "Published Date", "direction": "descending"}]

    posts: list[dict] = []
    async for page_obj in notion_client.query_database(filter=db_filter, sorts=sorts):
        meta = _extract_post_meta(page_obj)
        del meta["related_post_ids"]
        posts.append(meta)
        if len(posts) >= 3:
            break

    await cache_set(cache_k, posts)
    return posts


@router.get("/posts/{slug}")
async def get_post(slug: str, lang: str = Query("")):
    """Get a single blog post by slug with rendered HTML content."""
    lang = _validate_lang(lang)
    cache_k = post_key(lang, slug)
    cached = await cache_get(cache_k)
    if cached:
        return cached

    # Find the post by slug and language
    db_filter = {
        "and": [
            {"property": "Published", "checkbox": {"equals": True}},
            {"property": "Slug", "rich_text": {"equals": slug}},
            {"property": "Language", "select": {"equals": lang}},
        ]
    }

    page_obj = None
    async for result in notion_client.query_database(filter=db_filter):
        page_obj = result
        break

    if not page_obj:
        raise HTTPException(status_code=404, detail="Post not found")

    # Fetch blocks and render
    try:
        blocks = await notion_client.get_blocks(page_obj["id"])
    except NotionNotFound:
        raise HTTPException(status_code=404, detail="Post content not found")

    meta = _extract_post_meta(page_obj)
    content_html = render_blocks(blocks)
    toc = extract_toc(blocks)
    reading_time = _estimate_reading_time(blocks)

    # Resolve related posts
    related_posts: list[dict] = []
    for rel_id in meta.get("related_post_ids", []):
        try:
            rel_page = await notion_client.get_page(rel_id)
            rel_meta = _extract_post_meta(rel_page)
            # Only include published posts
            rel_props = rel_page.get("properties", {})
            if _get_checkbox(rel_props.get("Published", {})):
                del rel_meta["related_post_ids"]
                related_posts.append(rel_meta)
        except Exception:
            continue

    # Remove internal field, add resolved related posts
    del meta["related_post_ids"]

    result = {
        **meta,
        "content_html": content_html,
        "table_of_contents": toc,
        "reading_time": reading_time,
        "related_posts": related_posts,
    }
    await cache_set(cache_k, result)
    return result


@router.get("/categories")
async def list_categories(lang: str = Query("")):
    """List all available categories from published posts."""
    lang = _validate_lang(lang)
    cache_k = categories_key(lang)
    cached = await cache_get(cache_k)
    if cached:
        return cached

    categories: set[str] = set()
    db_filter = {
        "and": [
            {"property": "Published", "checkbox": {"equals": True}},
            {"property": "Language", "select": {"equals": lang}},
        ]
    }
    async for page_obj in notion_client.query_database(filter=db_filter):
        cat = _get_select(page_obj.get("properties", {}).get("Category", {}))
        if cat:
            categories.add(cat)

    result = sorted(categories)
    await cache_set(cache_k, result)
    return result


@router.get("/tags")
async def list_tags(lang: str = Query("")):
    """List all tags used across published posts."""
    lang = _validate_lang(lang)
    cache_k = tags_key(lang)
    cached = await cache_get(cache_k)
    if cached:
        return cached

    tags: set[str] = set()
    db_filter = {
        "and": [
            {"property": "Published", "checkbox": {"equals": True}},
            {"property": "Language", "select": {"equals": lang}},
        ]
    }
    async for page_obj in notion_client.query_database(filter=db_filter):
        for tag in _get_multi_select(page_obj.get("properties", {}).get("Tags", {})):
            tags.add(tag)

    result = sorted(tags)
    await cache_set(cache_k, result)
    return result


# ── Static pages ───────────────────────────────────────────


@router.get("/pages/{page_slug}")
async def get_static_page(page_slug: str, lang: str = Query("")):
    """Get a static page by slug from the Pages database."""
    lang = _validate_lang(lang)
    cache_k = page_key(lang, page_slug)
    cached = await cache_get(cache_k)
    if cached:
        return cached

    if not settings.notion_pages_data_source_id:
        raise HTTPException(status_code=404, detail="Pages database not configured")

    db_filter = {
        "and": [
            {"property": "Slug", "rich_text": {"equals": page_slug}},
            {"property": "Language", "select": {"equals": lang}},
        ]
    }

    page_obj = None
    try:
        async for result in notion_client.query_database(
            data_source_id=settings.notion_pages_data_source_id, filter=db_filter
        ):
            page_obj = result
            break
    except NotionNotFound:
        raise HTTPException(status_code=404, detail="Pages database not accessible")
    except NotionAPIError:
        raise HTTPException(status_code=502, detail="Failed to query Pages database")

    if not page_obj:
        raise HTTPException(status_code=404, detail="Page not found")

    try:
        blocks = await notion_client.get_blocks(page_obj["id"])
    except NotionNotFound:
        raise HTTPException(status_code=404, detail="Page content not found")

    props = page_obj.get("properties", {})
    title = _get_plain_text(props.get("Name", {}))
    content_html = render_blocks(blocks)

    result = {
        "slug": page_slug,
        "title": title,
        "content_html": content_html,
    }
    await cache_set(cache_k, result)
    return result
