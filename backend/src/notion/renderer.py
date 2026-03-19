"""Convert Notion block trees into HTML strings."""

from html import escape
from typing import Any
from urllib.parse import parse_qs, urlparse


# ── Notion color → CSS mapping ──────────────────────────────

_COLORS = {
    "gray": "#787774",
    "brown": "#9F6B53",
    "orange": "#D9730D",
    "yellow": "#CB912F",
    "green": "#448361",
    "blue": "#337EA9",
    "purple": "#9065B0",
    "pink": "#C14C8A",
    "red": "#D44C47",
    "gray_background": "#F1F1EF",
    "brown_background": "#F4EEEE",
    "orange_background": "#FBECDD",
    "yellow_background": "#FBF3DB",
    "green_background": "#EDF3EC",
    "blue_background": "#E7F3F8",
    "purple_background": "#F6F3F9",
    "pink_background": "#F9F0F5",
    "red_background": "#FDEBEC",
}


def _color_style(color: str) -> str:
    if color == "default" or not color:
        return ""
    if color.endswith("_background"):
        css = _COLORS.get(color, "")
        return f' style="background-color:{css}"' if css else ""
    css = _COLORS.get(color, "")
    return f' style="color:{css}"' if css else ""


# ── Rich text rendering ────────────────────────────────────


def render_rich_text(rich_text_items: list[dict]) -> str:
    """Convert a Notion rich_text array into an HTML string."""
    parts: list[str] = []

    for item in rich_text_items:
        text = escape(item.get("plain_text", ""))
        if not text:
            continue

        annotations = item.get("annotations", {})
        href = item.get("href")
        item_type = item.get("type", "text")

        # Equation inline
        if item_type == "equation":
            expr = escape(item.get("equation", {}).get("expression", ""))
            parts.append(f'<span class="inline-equation" data-equation="{expr}">{expr}</span>')
            continue

        # Apply annotations
        if annotations.get("code"):
            text = f"<code>{text}</code>"
        if annotations.get("bold"):
            text = f"<strong>{text}</strong>"
        if annotations.get("italic"):
            text = f"<em>{text}</em>"
        if annotations.get("strikethrough"):
            text = f"<del>{text}</del>"
        if annotations.get("underline"):
            text = f"<u>{text}</u>"

        color = annotations.get("color", "default")
        if color and color != "default":
            css = _COLORS.get(color, "")
            if css:
                prop = "background-color" if color.endswith("_background") else "color"
                text = f'<span style="{prop}:{css}">{text}</span>'

        if href:
            text = f'<a href="{escape(href)}">{text}</a>'

        parts.append(text)

    return "".join(parts)


# ── File/image URL extraction ───────────────────────────────


def _get_file_url(file_obj: dict) -> str:
    """Extract URL from a Notion file object (type: file or external)."""
    ftype = file_obj.get("type", "")
    if ftype == "file":
        return file_obj.get("file", {}).get("url", "")
    if ftype == "external":
        return file_obj.get("external", {}).get("url", "")
    return ""


def _youtube_embed_url(url: str) -> str | None:
    """Convert a YouTube URL into an embeddable URL."""
    try:
        parsed = urlparse(url)
    except Exception:
        return None

    host = (parsed.netloc or "").lower().removeprefix("www.")
    video_id = ""

    if host in {"youtube.com", "m.youtube.com"}:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [""])[0]
        elif parsed.path.startswith("/embed/"):
            video_id = parsed.path.split("/embed/", 1)[1].split("/", 1)[0]
        elif parsed.path.startswith("/shorts/"):
            video_id = parsed.path.split("/shorts/", 1)[1].split("/", 1)[0]
    elif host == "youtu.be":
        video_id = parsed.path.lstrip("/").split("/", 1)[0]

    if not video_id:
        return None

    query = parse_qs(parsed.query)
    start = query.get("start", query.get("t", [""]))[0]
    embed_url = f"https://www.youtube-nocookie.com/embed/{escape(video_id)}"
    if start:
        embed_url += f"?start={escape(start)}"
    return embed_url


def _vimeo_embed_url(url: str) -> str | None:
    """Convert a Vimeo URL into an embeddable URL."""
    try:
        parsed = urlparse(url)
    except Exception:
        return None

    host = (parsed.netloc or "").lower().removeprefix("www.")
    if host == "player.vimeo.com" and parsed.path.startswith("/video/"):
        return url
    if host != "vimeo.com":
        return None

    video_id = parsed.path.strip("/").split("/", 1)[0]
    if not video_id.isdigit():
        return None
    return f"https://player.vimeo.com/video/{video_id}"


def _embed_url(url: str) -> str | None:
    """Return an iframe-safe embed URL for known providers."""
    return _youtube_embed_url(url) or _vimeo_embed_url(url)


def _is_twitter_url(url: str) -> bool:
    try:
        host = (urlparse(url).netloc or "").lower().removeprefix("www.")
    except Exception:
        return False
    return host in {"twitter.com", "x.com"}


def _render_iframe(url: str, title: str) -> str:
    safe_url = escape(url)
    safe_title = escape(title)
    return (
        "<iframe "
        f'src="{safe_url}" '
        f'title="{safe_title}" '
        'frameborder="0" '
        'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" '
        "allowfullscreen "
        'loading="lazy"></iframe>'
    )


# ── Block renderers ─────────────────────────────────────────


def _render_paragraph(block: dict) -> str:
    data = block.get("paragraph", {})
    text = render_rich_text(data.get("rich_text", []))
    color = _color_style(data.get("color", "default"))
    children = _render_children(block)
    return f"<p{color}>{text}</p>{children}"


def _render_heading(block: dict, level: int) -> str:
    key = f"heading_{level}"
    data = block.get(key, {})
    text = render_rich_text(data.get("rich_text", []))
    color = _color_style(data.get("color", "default"))
    block_id = block.get("id", "").replace("-", "")
    return f'<h{level} id="{block_id}"{color}>{text}</h{level}>'


def _render_bulleted_list_item(block: dict) -> str:
    data = block.get("bulleted_list_item", {})
    text = render_rich_text(data.get("rich_text", []))
    color = _color_style(data.get("color", "default"))
    children = _render_children(block)
    return f"<li{color}>{text}{children}</li>"


def _render_numbered_list_item(block: dict) -> str:
    data = block.get("numbered_list_item", {})
    text = render_rich_text(data.get("rich_text", []))
    color = _color_style(data.get("color", "default"))
    children = _render_children(block)
    return f"<li{color}>{text}{children}</li>"


def _render_to_do(block: dict) -> str:
    data = block.get("to_do", {})
    text = render_rich_text(data.get("rich_text", []))
    checked = "checked" if data.get("checked") else ""
    children = _render_children(block)
    return f'<li class="todo-item"><input type="checkbox" disabled {checked}> {text}{children}</li>'


def _render_toggle(block: dict) -> str:
    data = block.get("toggle", {})
    text = render_rich_text(data.get("rich_text", []))
    children = _render_children(block)
    return f"<details><summary>{text}</summary>{children}</details>"


def _render_quote(block: dict) -> str:
    data = block.get("quote", {})
    text = render_rich_text(data.get("rich_text", []))
    color = _color_style(data.get("color", "default"))
    children = _render_children(block)
    return f"<blockquote{color}>{text}{children}</blockquote>"


def _render_callout(block: dict) -> str:
    data = block.get("callout", {})
    text = render_rich_text(data.get("rich_text", []))
    icon = data.get("icon", {})
    icon_html = ""
    if icon.get("type") == "emoji":
        icon_html = f'<span class="callout-icon">{icon["emoji"]}</span>'
    color = _color_style(data.get("color", "default"))
    children = _render_children(block)
    return f'<div class="callout"{color}>{icon_html}<div class="callout-content">{text}{children}</div></div>'


def _render_code(block: dict) -> str:
    data = block.get("code", {})
    text = render_rich_text(data.get("rich_text", []))
    lang = escape(data.get("language", "plain text"))
    caption = render_rich_text(data.get("caption", []))
    html = f'<pre><code class="language-{lang}">{text}</code></pre>'
    if caption:
        html = f"<figure>{html}<figcaption>{caption}</figcaption></figure>"
    return html


def _render_equation(block: dict) -> str:
    data = block.get("equation", {})
    expr = escape(data.get("expression", ""))
    return f'<div class="equation" data-equation="{expr}">{expr}</div>'


def _render_divider(_block: dict) -> str:
    return "<hr>"


def _render_image(block: dict) -> str:
    data = block.get("image", {})
    url = escape(_get_file_url(data))
    caption = render_rich_text(data.get("caption", []))
    cap_html = f"<figcaption>{caption}</figcaption>" if caption else ""
    return (
        f'<figure><img src="{url}" alt="{escape(caption or "")}" loading="lazy">{cap_html}</figure>'
    )


def _render_video(block: dict) -> str:
    data = block.get("video", {})
    url = _get_file_url(data)
    caption = render_rich_text(data.get("caption", []))
    cap_html = f"<figcaption>{caption}</figcaption>" if caption else ""
    embed_url = _embed_url(url)
    if embed_url:
        return (
            f"<figure>{_render_iframe(embed_url, caption or 'Embedded video')}{cap_html}</figure>"
        )
    return f'<figure><video src="{escape(url)}" controls preload="metadata"></video>{cap_html}</figure>'


def _render_bookmark(block: dict) -> str:
    data = block.get("bookmark", {})
    url = escape(data.get("url", ""))
    caption = render_rich_text(data.get("caption", []))
    label = caption or url
    return f'<a class="bookmark" href="{url}" target="_blank" rel="noopener">{label}</a>'


def _render_embed(block: dict) -> str:
    data = block.get("embed", {})
    caption = render_rich_text(data.get("caption", []))
    cap_html = f"<figcaption>{caption}</figcaption>" if caption else ""

    # Use pre-fetched oEmbed HTML for Twitter/X posts (raw iframe would be
    # refused by X's X-Frame-Options: deny header).
    oembed_html = data.get("oembed_html", "")
    if oembed_html:
        return f'<figure class="embed-tweet">{oembed_html}{cap_html}</figure>'

    url = data.get("url", "")
    embed_url = _embed_url(url)
    if embed_url:
        return (
            f"<figure>{_render_iframe(embed_url, caption or 'Embedded content')}{cap_html}</figure>"
        )

    safe_url = escape(url)
    if _is_twitter_url(url):
        label = caption or safe_url
        return (
            f'<figure class="embed-tweet-fallback"><a href="{safe_url}" target="_blank" '
            f'rel="noopener noreferrer">{label}</a>{cap_html}</figure>'
        )

    return f"<figure>{_render_iframe(url, caption or 'Embedded content')}{cap_html}</figure>"


def _render_table(block: dict) -> str:
    children = block.get("children", [])
    if not children:
        return ""
    has_header = block.get("table", {}).get("has_column_header", False)
    rows: list[str] = []
    for i, row_block in enumerate(children):
        cells = row_block.get("table_row", {}).get("cells", [])
        tag = "th" if (i == 0 and has_header) else "td"
        cells_html = "".join(f"<{tag}>{render_rich_text(cell)}</{tag}>" for cell in cells)
        rows.append(f"<tr>{cells_html}</tr>")
    header = ""
    body_rows = rows
    if has_header and rows:
        header = f"<thead>{rows[0]}</thead>"
        body_rows = rows[1:]
    body = f"<tbody>{''.join(body_rows)}</tbody>"
    return f"<table>{header}{body}</table>"


def _render_column_list(block: dict) -> str:
    children = block.get("children", [])
    cols: list[str] = []
    for col_block in children:
        col_children = col_block.get("children", [])
        inner = render_blocks(col_children)
        cols.append(f'<div class="column">{inner}</div>')
    return f'<div class="columns">{"".join(cols)}</div>'


def _render_child_page(block: dict) -> str:
    data = block.get("child_page", {})
    title = escape(data.get("title", "Untitled"))
    page_id = block.get("id", "")
    return f'<a class="child-page" href="/blog/{page_id}">{title}</a>'


def _render_link_to_page(block: dict) -> str:
    data = block.get("link_to_page", {})
    page_id = data.get("page_id", "") or data.get("database_id", "")
    return f'<a class="link-to-page" href="/blog/{page_id}">Linked page</a>'


def _render_synced_block(block: dict) -> str:
    children = block.get("children", [])
    return render_blocks(children)


def _render_table_of_contents(_block: dict) -> str:
    # Frontend generates its own TOC from headings
    return ""


def _render_breadcrumb(_block: dict) -> str:
    return ""


# ── Children helper ─────────────────────────────────────────


def _render_children(block: dict) -> str:
    children = block.get("children", [])
    if not children:
        return ""
    return render_blocks(children)


# ── Block type dispatch ─────────────────────────────────────

_RENDERERS: dict[str, Any] = {
    "paragraph": _render_paragraph,
    "heading_1": lambda b: _render_heading(b, 1),
    "heading_2": lambda b: _render_heading(b, 2),
    "heading_3": lambda b: _render_heading(b, 3),
    "bulleted_list_item": _render_bulleted_list_item,
    "numbered_list_item": _render_numbered_list_item,
    "to_do": _render_to_do,
    "toggle": _render_toggle,
    "quote": _render_quote,
    "callout": _render_callout,
    "code": _render_code,
    "equation": _render_equation,
    "divider": _render_divider,
    "image": _render_image,
    "video": _render_video,
    "bookmark": _render_bookmark,
    "embed": _render_embed,
    "table": _render_table,
    "column_list": _render_column_list,
    "child_page": _render_child_page,
    "link_to_page": _render_link_to_page,
    "synced_block": _render_synced_block,
    "table_of_contents": _render_table_of_contents,
    "breadcrumb": _render_breadcrumb,
}

# Block types that need list grouping
_LIST_TYPES = {
    "bulleted_list_item": "ul",
    "numbered_list_item": "ol",
    "to_do": 'ul class="todo-list"',
}


def render_blocks(blocks: list[dict]) -> str:
    """Render a list of Notion blocks to HTML, grouping consecutive list items."""
    html_parts: list[str] = []
    i = 0

    while i < len(blocks):
        block = blocks[i]
        btype = block.get("type", "")

        # Group consecutive list items
        if btype in _LIST_TYPES:
            tag = _LIST_TYPES[btype]
            tag_name = tag.split()[0]  # "ul" or "ol"
            items: list[str] = []
            while i < len(blocks) and blocks[i].get("type") == btype:
                renderer = _RENDERERS.get(btype)
                if renderer:
                    items.append(renderer(blocks[i]))
                i += 1
            html_parts.append(f"<{tag}>{''.join(items)}</{tag_name}>")
            continue

        renderer = _RENDERERS.get(btype)
        if renderer:
            html_parts.append(renderer(block))
        # Unsupported block types are silently skipped

        i += 1

    return "\n".join(html_parts)


# ── Table of contents extraction ────────────────────────────


def extract_toc(blocks: list[dict]) -> list[dict]:
    """Extract heading blocks into a flat TOC list."""
    toc: list[dict] = []

    for block in blocks:
        btype = block.get("type", "")
        if btype in ("heading_1", "heading_2", "heading_3"):
            level = int(btype[-1])
            data = block.get(btype, {})
            text = "".join(item.get("plain_text", "") for item in data.get("rich_text", []))
            block_id = block.get("id", "").replace("-", "")
            toc.append({"id": block_id, "text": text, "level": level})

        # Recurse into children
        children = block.get("children", [])
        if children:
            toc.extend(extract_toc(children))

    return toc
