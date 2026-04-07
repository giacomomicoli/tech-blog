# Notion SEO Manual Setup

This document lists the manual Notion steps required after the SEO foundation changes in code.

Use `docs/notion-setup.md` for database creation and baseline property setup.
Use this file for SEO-specific backfill, editorial conventions, and validation.

## Databases To Update

- `Posts`
- `Pages`

## Properties To Add

### Posts

| Property Name | Type | Required | Why it matters |
|---------------|------|----------|----------------|
| `Translation Key` | Rich Text | Yes | Links localized versions of the same article so the site can emit reliable `hreflang` alternates |
| `Meta Description` | Rich Text | Recommended | Overrides the search/social snippet; falls back to `Excerpt` when empty |
| `Social Image` | URL | Recommended | Overrides the social preview image used by Open Graph, Twitter, and JSON-LD |

### Pages

| Property Name | Type | Required | Why it matters |
|---------------|------|----------|----------------|
| `Translation Key` | Rich Text | Yes | Links localized versions of the same static page |
| `Meta Description` | Rich Text | Strongly recommended | Controls snippets and page-level structured data description |
| `Social Image` | URL | Recommended | Overrides the default TECH.md social card for static pages |

## How To Fill `Translation Key`

`Translation Key` is an internal stable identifier shared by all real translations of the same content.

Rules:

1. Use exactly the same value across all locale versions of the same post or page.
2. Do not add locale suffixes such as `-it` or `-en`.
3. Keep the value stable over time even if one slug changes.
4. Reuse a key only for true translations, never for loosely related content.
5. For built-in static pages, keep the slug identical across locales and use the slug itself as the translation key.

Examples for TECH.md:

| Content | Language | Slug | Translation Key |
|---------|----------|------|-----------------|
| Article | `it` | `guida-docker-swarm` | `docker-swarm-guide` |
| Article | `en` | `docker-swarm-guide` | `docker-swarm-guide` |
| Page | `it` | `about-blog` | `about-blog` |
| Page | `en` | `about-blog` | `about-blog` |

Invalid example:

| Language | Slug | Translation Key |
|----------|------|-----------------|
| `it` | `guida-docker-swarm` | `docker-swarm-guide-it` |
| `en` | `docker-swarm-guide` | `docker-swarm-guide-en` |

The application would not consider these entries translations of each other.

## How To Fill `Meta Description`

Write one description per language.
Aim for a short, readable summary that explains what the content is and why it is useful.

Guidelines:

1. Target roughly 140 to 160 characters.
2. Avoid repeating the title verbatim unless it improves clarity.
3. Avoid keyword stuffing.
4. Keep the description faithful to the actual content.
5. If you leave the field empty on posts, make sure `Excerpt` is still editorially strong because it becomes the SEO fallback.

TECH.md examples:

EN article:

`A practical guide to Docker Swarm for small production stacks, covering deployment flow, secrets, networking, and the tradeoffs that matter in real projects.`

IT article:

`Una guida pratica a Docker Swarm per stack di produzione contenute, con focus su deploy, segreti, networking e compromessi reali.`

EN `about-blog`:

`TECH.md is a multilingual Notion-powered tech blog focused on practical software engineering notes, tutorials, and curated technical writing.`

IT `about-blog`:

`TECH.md e un blog tech multilingua basato su Notion, dedicato a tutorial, note di ingegneria del software e scrittura tecnica curata.`

## How To Fill `Social Image`

Use `Social Image` only when the default fallback is not good enough.

Current image fallback in code:

1. `Social Image`
2. `Cover`
3. repo fallback image: `frontend/public/social/default-social-card.png`

Rules:

1. Use a stable, public, absolute `https://` URL.
2. Prefer images at least `1200x630`.
3. Avoid temporary or expiring Notion file URLs.
4. Use locale-specific images only when the image itself contains localized text.
5. Leave the field empty if the cover image already works well for sharing.

## Static Pages That Must Exist

The frontend already expects these slugs in every supported locale:

| Name | Slug | Locales |
|------|------|---------|
| About This Blog | `about-blog` | `it`, `en` |
| About Me | `about-me` | `it`, `en` |

Do not localize these slugs.
Only localize the page title and page body content.

## What The App Generates Automatically

Once the fields are present and filled, the application automatically generates:

- canonical URLs
- `hreflang` alternates for translated posts and static pages
- Open Graph tags
- Twitter tags
- JSON-LD for `WebSite`, `BlogPosting`, `CollectionPage`, `AboutPage` / `WebPage`, and breadcrumbs
- sitemap `lastmod` using Notion `last_edited_time`

You do not need to create JSON-LD fields in Notion.

## Recommended Backfill Order

1. Add `Translation Key` to `Posts`.
2. Add `Translation Key` to `Pages`.
3. Backfill all already-published translated entries.
4. Add `Meta Description` to the `Pages` database and fill `about-blog` / `about-me` first.
5. Improve post `Meta Description` where the excerpt is weak.
6. Add `Social Image` only where needed.

## Validation Checklist

After updating Notion:

1. Open one translated article in each locale and confirm both entries share the same `Translation Key`.
2. Open `about-blog` and `about-me` in each locale and confirm the `Translation Key` is stable and shared.
3. Confirm the `Meta Description` fields are filled for static pages that should rank.
4. Confirm any `Social Image` URL opens publicly without Notion authentication.
5. Inspect one page source per content type and verify:
   - canonical URL
   - `hreflang` links
   - `og:image`
   - `application/ld+json`
6. Check `/robots.txt` and `/sitemap.xml` on the deployed domain after rollout.
