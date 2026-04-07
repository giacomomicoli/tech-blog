# Notion Database Setup

This document describes the required databases and properties in your Notion workspace.

Use this file as the schema reference.
For editorial backfill rules and post-deploy validation steps related to SEO, see
`docs/notion-seo-manual-setup.md`.

## Finding Your Notion IDs

This project requires several different Notion IDs. They look similar (all UUIDs) but serve different purposes and are found in different places.

### ID Types at a Glance

| ID | Format | Where It Goes | How It's Used |
|----|--------|---------------|---------------|
| **API Key** | `ntn_...` (long token) | `NOTION_API_KEY` | Authenticates all API requests |
| **Database ID** | UUID (`xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`) | `NOTION_DATABASE_ID` | Identifies the Posts database (informational, not used in queries) |
| **Data Source ID** | UUID | `NOTION_DATA_SOURCE_ID` | Used to query the Posts database via `POST /v1/data_sources/{id}/query` |
| **Pages Data Source ID** | UUID | `NOTION_PAGES_DATA_SOURCE_ID` | Used to query the Pages database (same endpoint pattern) |
| **Page ID** | UUID | Returned by API, not configured | Identifies individual pages/posts (used internally for block fetching, related posts) |
| **Block ID** | UUID | Returned by API, not configured | Identifies content blocks within a page (used for TOC anchors, recursive fetching) |

### How to Find the API Key

1. Go to [notion.so/profile/integrations](https://www.notion.so/profile/integrations)
2. Click **New integration** (or open an existing one)
3. Give it a name (e.g. "Tech Blog"), select the workspace, and set capabilities to **Read content**
4. Click **Submit** → copy the **Internal Integration Secret** (starts with `ntn_`)
5. This goes in `NOTION_API_KEY`

### How to Find the Database ID

The database ID is visible in the Notion URL when you open a database as a full page:

```
https://www.notion.so/<workspace>/<database-id>?v=<view-id>
                                  ^^^^^^^^^^^^
```

For example:
```
https://www.notion.so/myworkspace/a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4?v=...
                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                  This is the database ID
```

The ID is the 32-character hex string (without hyphens in the URL, but the API accepts both formats). This goes in `NOTION_DATABASE_ID`.

### How to Find the Data Source ID

The data source ID is **not the same** as the database ID. It's required by the Notion API v2025-09-03 for the `/v1/data_sources/{id}/query` endpoint.

To retrieve it using the Notion API:

1. Make sure the database is shared with your integration (in Notion: click **...** on the database → **Add connections** → select your integration)
2. Call the Notion search endpoint to find your database:
   ```bash
   curl -X POST 'https://api.notion.com/v1/search' \
     -H 'Authorization: Bearer ntn_YOUR_API_KEY' \
     -H 'Notion-Version: 2025-09-03' \
     -H 'Content-Type: application/json' \
     -d '{"filter": {"value": "database", "property": "object"}}'
   ```
3. In the response, each database object has a `data_source` field:
   ```json
   {
     "object": "database",
     "id": "a1b2c3d4-...",
     "data_source": {
       "type": "database_id",
       "database_id": "a1b2c3d4-...",
       "data_source_id": "ds-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
     }
   }
   ```
4. Copy the `data_source_id` value — this goes in `NOTION_DATA_SOURCE_ID` (for Posts) or `NOTION_PAGES_DATA_SOURCE_ID` (for Pages)

**Tip**: If you have multiple databases, match them by comparing the `id` field with the database ID you found in the URL.

### How to Find Page IDs

You don't need to configure page IDs — they're returned by the API when querying databases. However, you can find them in Notion URLs:

```
https://www.notion.so/<workspace>/<page-title>-<page-id>
                                               ^^^^^^^^^
```

For example:
```
https://www.notion.so/myworkspace/My-First-Post-a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4
                                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                                                This is the page ID
```

Page IDs are used internally by the backend to:
- Fetch blocks for rendering (`GET /v1/blocks/{page_id}/children`)
- Resolve related posts (`GET /v1/pages/{page_id}`)

### How to Find Block IDs

Block IDs are internal — you never need to configure them. They're returned by the Notion API when fetching page content. Each block (paragraph, heading, image, etc.) has a unique UUID.

In the frontend, heading block IDs (with hyphens removed) are used as HTML `id` attributes for the Table of Contents anchor links.

### Sharing Databases with Your Integration

Both the Posts and Pages databases must be shared with your integration before the API can access them:

1. Open the database in Notion
2. Click **...** (three dots menu) in the top-right
3. Click **Add connections**
4. Select your integration from the list
5. Confirm the connection

If you forget this step, the API will return 404 errors when trying to query the database.

---

## Posts Database

The main database for blog posts.

### Required Properties

| Property Name    | Type         | Description                                    |
|------------------|--------------|------------------------------------------------|
| Name             | Title        | Post title                                     |
| Slug             | Rich Text    | URL-friendly identifier (e.g. `my-first-post`) |
| Excerpt          | Rich Text    | Short summary shown on post cards              |
| Category         | Select       | Single category per post                       |
| Tags             | Multi-select | One or more tags                               |
| Published Date   | Date         | Publication date                               |
| Cover            | URL          | Cover image URL                                |
| Author           | Rich Text    | Author name                                    |
| Published        | Checkbox     | Must be checked for the post to appear on site |
| Featured         | Checkbox     | Check to show post in the homepage hero carousel |
| Hero Position    | Number       | Position in homepage hero section (1-5). 1 = large tile, 2-5 = small tiles. Leave empty to exclude. |
| Top              | Checkbox     | Check to feature in the "Top Read" sidebar (up to 3 posts shown) |
| Related Posts    | Relation     | Self-referencing relation to other posts in the same database. Shown on post detail page. |
| Language         | Select       | Language code (e.g. `it`, `en`) — each post belongs to one language |

### Recommended SEO Properties

| Property Name    | Type      | Description |
|------------------|-----------|-------------|
| Translation Key  | Rich Text | Shared identifier across localized versions of the same post |
| Meta Description | Rich Text | Optional SEO description override; falls back to `Excerpt` |
| Social Image     | URL       | Optional social preview override for Open Graph / Twitter |

### Adding the Language Property

1. Open your Notion posts database
2. Click **+** to add a new property
3. Set **Name** to `Language` and **Type** to `Select`
4. Add options for each supported locale (e.g. `it`, `en`)
5. Set the `Language` property on each post to its content language

When creating multilingual content, duplicate the post and set each copy to a different language. Each language version should have its own language-specific slug (e.g. `il-mio-post` for Italian, `my-post` for English) for best SEO.

### Adding the Featured Property

1. Open your Notion posts database
2. Click **+** to add a new property
3. Set **Name** to `Featured` and **Type** to `Checkbox`
4. Check the box on any posts you want to appear in the hero carousel

Posts marked as Featured (with a cover image) will rotate in the homepage hero section. If no posts are featured, the hero section is hidden and the page shows the normal post grid.

### Adding the Hero Position Property

1. Open your Notion posts database
2. Click **+** to add a new property
3. Set **Name** to `Hero Position` and **Type** to `Number`
4. Set a number from 1 to 5 on posts you want in the hero section. Position 1 is the large tile on the left, positions 2-5 are the smaller tiles in a 2x2 grid on the right.

### Adding the Top Property

1. Open your Notion posts database
2. Click **+** to add a new property
3. Set **Name** to `Top` and **Type** to `Checkbox`
4. Check the box on up to 3 posts you want to appear in the "Top Read" sidebar on the homepage

### Adding the Related Posts Property

1. Open your Notion posts database
2. Click **+** to add a new property
3. Set **Name** to `Related Posts` and **Type** to `Relation`
4. Select the **same Posts database** (self-referencing relation)
5. On any post, add links to related posts. These will appear at the bottom of the post detail page.

---

## Pages Database

A separate database for static content pages (About This Blog, About Me, etc.). This is queried by the `GET /api/pages/{slug}` endpoint.

### Required Properties

| Property Name | Type      | Description                                         |
|---------------|-----------|-----------------------------------------------------|
| Name          | Title     | Page title (displayed as the page heading)          |
| Slug          | Rich Text | URL identifier — must match the frontend route slug |
| Language      | Select    | Language code (e.g. `it`, `en`) — same options as Posts |

### Recommended SEO Properties

| Property Name    | Type      | Description |
|------------------|-----------|-------------|
| Translation Key  | Rich Text | Shared identifier across localized versions of the same page |
| Meta Description | Rich Text | SEO description used for snippets and social previews |
| Social Image     | URL       | Optional social preview override for Open Graph / Twitter |

### Setup Steps

1. In Notion, create a new **full-page database** (e.g. inside your Blog root page)
2. Name it **"Pages"**
3. Add a **Rich Text** property called `Slug`
4. Add a **Select** property called `Language` with the same locale options as the Posts database
5. Share the database with your integration (see [Sharing Databases with Your Integration](#sharing-databases-with-your-integration) above)
6. Get the **data source ID** for this database using the search API (see [How to Find the Data Source ID](#how-to-find-the-data-source-id) above)
7. Set `NOTION_PAGES_DATA_SOURCE_ID` in your `.env` file to this ID

### Creating About Pages

Create entries in the Pages database for each language:

| Name              | Slug        | Language |
|-------------------|-------------|----------|
| About This Blog   | about-blog  | it       |
| About This Blog   | about-blog  | en       |
| About Me          | about-me    | it       |
| About Me          | about-me    | en       |

Then open each entry and write the page content using Notion's editor. The content is rendered to HTML the same way as blog posts (all block types supported).

Keep these built-in slugs identical across locales because the frontend routes are file-based and the SEO alternates assume stable page paths.

The frontend routes `/{lang}/about-blog` and `/{lang}/about-me` fetch from `/api/pages/about-blog?lang={lang}` and `/api/pages/about-me?lang={lang}` respectively.

### Adding More Pages

You can add any static page by creating a new entry in the Pages database with a unique slug. The backend endpoint `GET /api/pages/{slug}` accepts any slug — just create a matching frontend route.
