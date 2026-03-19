"""Tests for the Notion block-to-HTML renderer."""

from src.notion.renderer import extract_toc, render_blocks, render_rich_text


# ── Helpers ────────────────────────────────────────────────


def _rt(text: str, **annotations) -> dict:
    """Build a rich_text item."""
    return {
        "type": "text",
        "plain_text": text,
        "annotations": {
            "bold": False,
            "italic": False,
            "strikethrough": False,
            "underline": False,
            "code": False,
            "color": "default",
            **annotations,
        },
        "href": None,
    }


def _block(btype: str, rich_text: list[dict] | None = None, **extra) -> dict:
    """Build a minimal Notion block."""
    data = {}
    if rich_text is not None:
        data["rich_text"] = rich_text
    data.update(extra)
    return {"type": btype, btype: data, "id": "abc-123"}


# ── Rich text ──────────────────────────────────────────────


class TestRenderRichText:
    def test_plain_text(self):
        result = render_rich_text([_rt("Hello world")])
        assert result == "Hello world"

    def test_bold(self):
        result = render_rich_text([_rt("bold", bold=True)])
        assert "<strong>bold</strong>" in result

    def test_italic(self):
        result = render_rich_text([_rt("italic", italic=True)])
        assert "<em>italic</em>" in result

    def test_strikethrough(self):
        result = render_rich_text([_rt("gone", strikethrough=True)])
        assert "<del>gone</del>" in result

    def test_underline(self):
        result = render_rich_text([_rt("under", underline=True)])
        assert "<u>under</u>" in result

    def test_inline_code(self):
        result = render_rich_text([_rt("x = 1", code=True)])
        assert "<code>x = 1</code>" in result

    def test_link(self):
        item = _rt("click me")
        item["href"] = "https://example.com"
        result = render_rich_text([item])
        assert '<a href="https://example.com">click me</a>' in result

    def test_colored_text(self):
        result = render_rich_text([_rt("red text", color="red")])
        assert 'style="color:#D44C47"' in result

    def test_background_color(self):
        result = render_rich_text([_rt("highlight", color="yellow_background")])
        assert 'style="background-color:#FBF3DB"' in result

    def test_combined_annotations(self):
        result = render_rich_text([_rt("bold italic", bold=True, italic=True)])
        assert "<strong>" in result
        assert "<em>" in result

    def test_escapes_html(self):
        result = render_rich_text([_rt("<script>alert(1)</script>")])
        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_equation_inline(self):
        item = {"type": "equation", "plain_text": "E=mc²", "equation": {"expression": "E=mc²"}}
        result = render_rich_text([item])
        assert 'class="inline-equation"' in result
        assert "E=mc²" in result

    def test_empty_list(self):
        assert render_rich_text([]) == ""


# ── Block rendering ────────────────────────────────────────


class TestRenderBlocks:
    def test_paragraph(self):
        blocks = [_block("paragraph", [_rt("Hello")])]
        result = render_blocks(blocks)
        assert "<p>Hello</p>" in result

    def test_heading_levels(self):
        for level in (1, 2, 3):
            blocks = [_block(f"heading_{level}", [_rt(f"H{level}")])]
            result = render_blocks(blocks)
            assert f"<h{level}" in result
            assert f"H{level}</h{level}>" in result

    def test_heading_has_id(self):
        blocks = [_block("heading_2", [_rt("Title")])]
        result = render_blocks(blocks)
        assert 'id="abc123"' in result

    def test_bulleted_list_grouping(self):
        blocks = [
            _block("bulleted_list_item", [_rt("A")]),
            _block("bulleted_list_item", [_rt("B")]),
        ]
        result = render_blocks(blocks)
        assert result.count("<ul>") == 1
        assert result.count("</ul>") == 1
        assert result.count("<li>") == 2

    def test_numbered_list_grouping(self):
        blocks = [
            _block("numbered_list_item", [_rt("One")]),
            _block("numbered_list_item", [_rt("Two")]),
        ]
        result = render_blocks(blocks)
        assert result.count("<ol>") == 1
        assert result.count("</ol>") == 1

    def test_todo_list(self):
        blocks = [
            _block("to_do", [_rt("Task")], checked=True),
            _block("to_do", [_rt("Other")], checked=False),
        ]
        result = render_blocks(blocks)
        assert 'class="todo-list"' in result
        assert "checked" in result
        assert result.count("todo-item") == 2

    def test_separate_lists_not_merged(self):
        blocks = [
            _block("bulleted_list_item", [_rt("A")]),
            _block("paragraph", [_rt("Break")]),
            _block("bulleted_list_item", [_rt("B")]),
        ]
        result = render_blocks(blocks)
        assert result.count("<ul>") == 2

    def test_quote(self):
        blocks = [_block("quote", [_rt("Wise words")])]
        result = render_blocks(blocks)
        assert "<blockquote>" in result
        assert "Wise words" in result

    def test_callout_with_emoji(self):
        block = _block("callout", [_rt("Note!")], icon={"type": "emoji", "emoji": "💡"})
        result = render_blocks([block])
        assert 'class="callout"' in result
        assert "💡" in result
        assert "Note!" in result

    def test_code_block(self):
        block = _block("code", [_rt("print('hi')")], language="python", caption=[])
        result = render_blocks([block])
        assert 'class="language-python"' in result
        assert "print(&#x27;hi&#x27;)" in result

    def test_code_block_with_caption(self):
        block = _block("code", [_rt("x = 1")], language="python", caption=[_rt("Example")])
        result = render_blocks([block])
        assert "<figcaption>Example</figcaption>" in result

    def test_divider(self):
        blocks = [_block("divider")]
        result = render_blocks(blocks)
        assert "<hr>" in result

    def test_image_external(self):
        block = {
            "type": "image",
            "id": "img1",
            "image": {
                "type": "external",
                "external": {"url": "https://example.com/img.jpg"},
                "caption": [],
            },
        }
        result = render_blocks([block])
        assert '<img src="https://example.com/img.jpg"' in result
        assert 'loading="lazy"' in result

    def test_image_with_caption(self):
        block = {
            "type": "image",
            "id": "img2",
            "image": {
                "type": "external",
                "external": {"url": "https://example.com/img.jpg"},
                "caption": [_rt("A photo")],
            },
        }
        result = render_blocks([block])
        assert "<figcaption>A photo</figcaption>" in result

    def test_video_youtube(self):
        block = {
            "type": "video",
            "id": "vid1",
            "video": {
                "type": "external",
                "external": {"url": "https://youtube.com/watch?v=abc"},
                "caption": [],
            },
        }
        result = render_blocks([block])
        assert "<iframe" in result
        assert 'src="https://www.youtube-nocookie.com/embed/abc"' in result

    def test_video_youtu_be(self):
        block = {
            "type": "video",
            "id": "vid2",
            "video": {
                "type": "external",
                "external": {"url": "https://youtu.be/abc?t=42"},
                "caption": [],
            },
        }
        result = render_blocks([block])
        assert 'src="https://www.youtube-nocookie.com/embed/abc?start=42"' in result

    def test_embed_generic_uses_iframe(self):
        block = {
            "type": "embed",
            "id": "emb1",
            "embed": {"url": "https://example.com/some-embed", "caption": []},
        }
        result = render_blocks([block])
        assert "<iframe" in result
        assert 'src="https://example.com/some-embed"' in result

    def test_embed_youtube_watch_url_uses_embed_src(self):
        block = {
            "type": "embed",
            "id": "emb1b",
            "embed": {
                "url": "https://www.youtube.com/watch?v=QFDz6q-Qthk&feature=youtu.be",
                "caption": [],
            },
        }
        result = render_blocks([block])
        assert "<iframe" in result
        assert 'src="https://www.youtube-nocookie.com/embed/QFDz6q-Qthk"' in result

    def test_embed_twitter_with_oembed_html(self):
        """When oembed_html is pre-fetched, it should be used instead of an iframe."""
        oembed = '<blockquote class="twitter-tweet"><a href="https://twitter.com/x/status/1">Tweet</a></blockquote>'
        block = {
            "type": "embed",
            "id": "emb2",
            "embed": {
                "url": "https://x.com/user/status/123",
                "caption": [],
                "oembed_html": oembed,
            },
        }
        result = render_blocks([block])
        assert "<iframe" not in result
        assert 'class="twitter-tweet"' in result
        assert 'class="embed-tweet"' in result

    def test_embed_twitter_with_oembed_html_and_caption(self):
        oembed = '<blockquote class="twitter-tweet"><a href="https://twitter.com/x/status/1">Tweet</a></blockquote>'
        block = {
            "type": "embed",
            "id": "emb3",
            "embed": {
                "url": "https://twitter.com/user/status/456",
                "caption": [_rt("A tweet")],
                "oembed_html": oembed,
            },
        }
        result = render_blocks([block])
        assert "<figcaption>A tweet</figcaption>" in result
        assert 'class="twitter-tweet"' in result

    def test_embed_twitter_without_oembed_falls_back_to_iframe(self):
        """If oEmbed fetch failed, fall back to a plain outbound link."""
        block = {
            "type": "embed",
            "id": "emb4",
            "embed": {"url": "https://x.com/user/status/789", "caption": []},
        }
        result = render_blocks([block])
        assert "<iframe" not in result
        assert 'href="https://x.com/user/status/789"' in result
        assert 'class="embed-tweet-fallback"' in result

    def test_toggle(self):
        block = _block("toggle", [_rt("Click me")])
        result = render_blocks([block])
        assert "<details>" in result
        assert "<summary>Click me</summary>" in result

    def test_equation_block(self):
        block = _block("equation", expression="x^2 + y^2 = z^2")
        result = render_blocks([block])
        assert 'class="equation"' in result

    def test_table(self):
        block = {
            "type": "table",
            "id": "t1",
            "table": {"has_column_header": True},
            "children": [
                {"type": "table_row", "table_row": {"cells": [[_rt("Name")], [_rt("Age")]]}},
                {"type": "table_row", "table_row": {"cells": [[_rt("Alice")], [_rt("30")]]}},
            ],
        }
        result = render_blocks([block])
        assert "<thead>" in result
        assert "<th>Name</th>" in result
        assert "<td>Alice</td>" in result

    def test_column_list(self):
        block = {
            "type": "column_list",
            "id": "cl1",
            "column_list": {},
            "children": [
                {"type": "column", "column": {}, "children": [_block("paragraph", [_rt("Left")])]},
                {"type": "column", "column": {}, "children": [_block("paragraph", [_rt("Right")])]},
            ],
        }
        result = render_blocks([block])
        assert 'class="columns"' in result
        assert result.count('class="column"') == 2

    def test_unsupported_block_skipped(self):
        blocks = [
            {"type": "unsupported_type", "unsupported_type": {}, "id": "x"},
            _block("paragraph", [_rt("After")]),
        ]
        result = render_blocks(blocks)
        assert "After" in result
        assert "unsupported" not in result.lower()

    def test_nested_children(self):
        block = _block("paragraph", [_rt("Parent")])
        block["children"] = [_block("paragraph", [_rt("Child")])]
        result = render_blocks([block])
        assert "Parent" in result
        assert "Child" in result

    def test_empty_blocks(self):
        assert render_blocks([]) == ""


# ── TOC extraction ─────────────────────────────────────────


class TestExtractToc:
    def test_extracts_headings(self):
        blocks = [
            _block("heading_1", [_rt("Intro")]),
            _block("paragraph", [_rt("text")]),
            _block("heading_2", [_rt("Details")]),
        ]
        toc = extract_toc(blocks)
        assert len(toc) == 2
        assert toc[0] == {"id": "abc123", "text": "Intro", "level": 1}
        assert toc[1] == {"id": "abc123", "text": "Details", "level": 2}

    def test_recurses_into_children(self):
        block = _block("toggle", [_rt("Toggle")])
        block["children"] = [_block("heading_3", [_rt("Nested heading")])]
        toc = extract_toc([block])
        assert len(toc) == 1
        assert toc[0]["text"] == "Nested heading"
        assert toc[0]["level"] == 3

    def test_empty_blocks(self):
        assert extract_toc([]) == []
