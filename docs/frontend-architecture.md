# Frontend Architecture

> Authoritative reference for AI agents and developers. This document describes the current
> implementation of the frontend. Do not deviate from these patterns, component structures,
> naming conventions, or styling approaches when making changes.

## Structure

```
frontend/
├── app.vue                      # Root: NuxtLoadingIndicator + NuxtLayout + NuxtPage + site-wide WebSite JSON-LD
├── nuxt.config.ts               # SSR, theme loading, i18n, runtime config, transitions, meta
├── locales/
│   ├── it.json                  # Italian UI translations
│   └── en.json                  # English UI translations
├── layouts/
│   └── default.vue              # Header (NavBar) + main slot + footer
├── components/
│   ├── NavBar.vue               # Site navigation with categories dropdown and language switcher
│   ├── PostCard.vue             # Blog post preview card
│   ├── PostMeta.vue             # Post metadata (date, author, category, tags)
│   ├── HeroCarousel.vue         # Featured posts carousel (legacy)
│   ├── HeroSection.vue          # Hero tile grid (1 large + 4 small)
│   ├── TopRead.vue              # Top Read sidebar widget
│   ├── RelatedPosts.vue         # Related articles grid
│   └── TableOfContents.vue      # Sticky heading navigation sidebar
├── pages/
│   ├── index.vue                # Root redirect to /{defaultLocale}
│   └── [lang]/
│       ├── index.vue            # Homepage: hero carousel + post grid
│       ├── blog/[slug].vue      # Full post with content + TOC sidebar
│       ├── category/[name].vue  # Posts filtered by category
│       ├── tag/[name].vue       # Posts filtered by tag
│       ├── about-blog.vue       # Static "About This Blog" page
│       └── about-me.vue         # Static "About Me" page
├── composables/
│   ├── useApi.ts                # API client with server/client URL switching
│   ├── useLocaleSwitch.ts       # Locale switching helpers with alternate-aware fallbacks
│   └── useSeo.ts                # Shared canonical/meta/JSON-LD helpers
├── types/
│   └── blog.ts                  # TypeScript interfaces: Post, StaticPage, TocEntry, PostList
├── server/routes/
│   ├── rss.xml.ts               # RSS 2.0 feed generation
│   ├── robots.txt.ts            # Runtime robots.txt generation
│   └── sitemap.xml.ts           # XML sitemap generation
├── assets/
│   ├── css/
│   │   ├── main.css             # Global reset, typography, transitions, scrollbar
│   │   └── notion-content.css   # Styles for rendered Notion HTML blocks
│   └── themes/
│       ├── tech-dark/theme.css  # Tech dark theme (default)
│       ├── tech-light/theme.css # Tech light theme
│       ├── yarb-dark/theme.css  # YARB dark theme
│       └── yarb-light/theme.css # YARB light theme
├── public/
│   └── social/default-social-card.png  # Repo-level fallback share image for TECH.md
├── tests/composables/
│   ├── useLocaleSwitch.test.ts
│   └── useSeo.test.ts
├── tests/components/
│   ├── PostCard.test.ts
│   ├── PostMeta.test.ts
│   ├── TableOfContents.test.ts
│   ├── HeroSection.test.ts
│   ├── TopRead.test.ts
│   └── RelatedPosts.test.ts
├── Dockerfile                   # Multi-stage: node:20-alpine, 3 stages
└── docker-entrypoint.dev.sh     # Dev: runs npm install before starting
```

## Nuxt Configuration

### SSR

SSR is enabled. The frontend renders server-side for SEO, then hydrates on the client.

### Runtime Config

```typescript
runtimeConfig: {
    backendUrl: process.env.BACKEND_URL || 'http://backend:8000',  // server-side only
    public: {
        backendUrl: process.env.NUXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',  // client-side
        siteUrl: process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost:3000',
        defaultLocale: process.env.DEFAULT_LOCALE || 'it',
        supportedLocales: process.env.SUPPORTED_LOCALES || 'it,en',
    }
}
```

In production, `NUXT_PUBLIC_BACKEND_URL` is set to `/api` (relative path) because
Caddy proxies `/api/*` to the backend. The frontend never exposes the backend's internal port.

### i18n (`@nuxtjs/i18n`)

The `@nuxtjs/i18n` module handles locale routing, translations, and locale detection.

- **Strategy**: `prefix` — all locales use URL prefix (`/it/...`, `/en/...`)
- **Default locale**: From `DEFAULT_LOCALE` env var (default: `it`)
- **Supported locales**: Built from `SUPPORTED_LOCALES` env var at build time
- **Browser detection**: Disabled (`detectBrowserLanguage: false`)
- **Locale files**: `frontend/locales/{code}.json` loaded via `langDir` config
- **Lazy loading**: Enabled for locale files

Root `/` redirects to `/{defaultLocale}` via `pages/index.vue`.

### CSS Loading Order

1. Theme file: `~/assets/themes/{NUXT_THEME}/theme.css` (CSS custom properties)
2. Main styles: `~/assets/css/main.css` (global reset, typography, transitions)
3. Notion styles: `~/assets/css/notion-content.css` (rendered Notion block styling)

### App-Level Meta

```typescript
head: {
    charset: 'utf-8',
    viewport: 'width=device-width, initial-scale=1',
    title: 'TECH.md',
    titleTemplate: '%s | TECH.md',
    meta: [{ name: 'description', content: 'TECH.md is a multilingual Notion-powered tech blog focused on clear writing, practical insights, and curated developer content.' }],
    link: [
        // Google Fonts: Atkinson Hyperlegible Mono
        // RSS feed: /rss.xml
    ]
}
```

The home page overrides `titleTemplate` to empty string so the title is just "TECH.md"
without the suffix.

### Shared SEO Layer

`frontend/composables/useSeo.ts` centralizes:

- canonical URL generation from runtime `siteUrl`
- `hreflang` alternate link emission
- Open Graph and Twitter metadata
- fallback image resolution (`social_image -> cover_image -> default social card`)
- fallback descriptions for static pages via HTML summarization
- JSON-LD builders for `WebSite`, `CollectionPage`, `BlogPosting`, `AboutPage` / `WebPage`, and breadcrumbs

### Page Transitions

```typescript
pageTransition: { name: 'page', mode: 'out-in' }
```

CSS in `main.css`:
```css
.page-enter-active, .page-leave-active { transition: opacity var(--transition-base); }
.page-enter-from, .page-leave-to { opacity: 0; }
```

`--transition-base` is `250ms cubic-bezier(0.4, 0.0, 0.2, 1)`.

## Root Component (`app.vue`)

`app.vue` injects a site-wide `WebSite` JSON-LD block once through `useSeo()` and still wraps all
pages in the default layout with the global loading indicator.

- Loading indicator: 3px bar at top of page, uses theme accent color
- All pages wrapped in the default layout

## Layout (`layouts/default.vue`)

Structure: `.site` → `.site-header` (NavBar) + `.site-main` (slot) + `.site-footer`.

- `.site` is a flex column with `min-height: 100vh` to push the footer down
- Footer text uses `$t('footer.text', { year })` for i18n support

## Components

### NavBar.vue

Site navigation with responsive mobile/desktop layout and language switcher.

**Structure**: Brand link ("TECH.md") + hamburger toggle (mobile) + menu links + language switcher.

**Menu items**: Home, Categories (dropdown), About This Blog, About Me, Language links.

**State**:
- `menuOpen: ref(false)` — mobile menu visibility
- `dropdownOpen: ref(false)` — categories dropdown visibility

**Data fetching**: Categories fetched via `useAsyncData` with locale-specific key.

**i18n**: All labels use `$t()` for translations. Links are locale-prefixed (`/${locale}/...`).
The language switcher still falls back safely for taxonomy pages, but it now uses backend-provided
alternates for translated posts and static pages when available.

**Responsive behavior**:
- Mobile: Hamburger icon toggles menu. Menu is vertical. Categories dropdown nested inline.
- Desktop (768px+): Hamburger hidden. Menu is horizontal flex. Dropdown positioned absolute below trigger.

**CSS classes**: `.navbar`, `.navbar-toggle`, `.hamburger`, `.navbar-menu`, `.navbar-link`,
`.dropdown-trigger`, `.dropdown-menu`, `.dropdown-link`, `.navbar-lang`, `.navbar-link-lang`.

### PostCard.vue

Blog post preview card for grid/list layouts.

**Props**: `{ post: Post }`

**Features**: Cover image (16:9, lazy loaded), title link, publication date + author,
excerpt (line-clamped: 3 lines mobile, 2 lines tablet+), category badge, reading time, tag list, "Read More" button.
All text labels use `$t()`, all links are locale-prefixed (`/${locale}/...`).

**Responsive**: Stacked on mobile, side-by-side at 768px (280px fixed image), larger at 1024px (320px image).

**CSS classes**: `.post-preview`, `.post-preview-cover`, `.post-preview-body`, `.excerpt`,
`.post-preview-tags`, `.tag`.

### HeroCarousel.vue

Featured posts carousel/slider.

**Props**: `{ posts: Post[] }`

**Features**: Horizontal scroll snap, background cover images with dark gradient overlay,
auto-advance every 6 seconds (respects `prefers-reduced-motion`), dot navigation.

**Hardcoded colors**: White text (`#fff`), overlay gradient (`rgba(0,0,0,0.75)` to transparent),
excerpt text (`rgba(255,255,255,0.85)`). These are intentional — the hero always uses
dark overlay on images regardless of theme.

**CSS classes**: `.hero`, `.hero-track`, `.hero-slide`, `.hero-overlay`, `.hero-content`,
`.hero-title`, `.hero-excerpt`, `.hero-cta`, `.hero-dots`, `.hero-dot`.

### HeroSection.vue

Homepage hero tile grid with 1 large tile and up to 4 small tiles.

**Props**: `{ posts: Post[] }` (up to 5, sorted by hero_position)

**Layout**: Large tile (position 1) on the left, small tiles in a 2x2 grid on the right.
Each tile shows cover image as background, gradient overlay, title, category badge, and links to post.

**Responsive**: Desktop = side-by-side grid, tablet = large on top + 2x2 below, mobile = all stacked.

**CSS classes**: `.hero-section`, `.hero-grid`, `.hero-tile`, `.hero-tile--large`, `.hero-tile--small`,
`.hero-tile__link`, `.hero-tile__overlay`, `.hero-tile__content`, `.hero-tile__category`, `.hero-tile__title`,
`.hero-tile__date`, `.hero-small-grid`.

### TopRead.vue

Sidebar widget showing top-read posts.

**Props**: `{ posts: Post[] }` (up to 3)

**Renders**: Heading ("Top Read"), list of compact cards with thumbnail, title, and date.
Hidden when posts array is empty.

**CSS classes**: `.top-read`, `.top-read__heading`, `.top-read__list`, `.top-read__item`,
`.top-read__link`, `.top-read__thumb`, `.top-read__info`, `.top-read__title`, `.top-read__date`.

### RelatedPosts.vue

Related articles grid shown at bottom of post detail page.

**Props**: `{ posts: Post[] }`

**Renders**: Section heading ("Related Articles") + grid of PostCard components.
Hidden when posts array is empty.

**Responsive**: 1 column mobile, 2 columns tablet, 3 columns desktop.

**CSS classes**: `.related-posts`, `.related-posts__heading`, `.related-posts__grid`.

### PostMeta.vue

Post metadata display.

**Props**: `{ post: Post }`

**Renders**: Publication date (formatted via `toLocaleDateString(locale.value, ...)`),
author byline (`$t('post.by')`), reading time (`$t('post.minRead')`), category link (locale-prefixed), tag list (locale-prefixed links).

**CSS classes**: `.post-meta`, `.post-meta-top`, `.post-meta-bottom`, `.byline`,
`.reading-time`, `.post-meta-category`, `.post-meta-tags`, `.tag`.

### TableOfContents.vue

Sticky sidebar navigation for post headings.

**Props**: `{ entries: TocEntry[] }`

**Renders**: Only if `entries.length > 0`. Heading text uses `$t('toc.title')` + anchor links.
Level 3 headings are indented relative to level 2.

**CSS classes**: `.toc`, `.toc-title`, `.toc-list`, `.toc-item`, `.toc-level-2`,
`.toc-level-3`, `.toc-link`.

## Pages

### index.vue (Root Redirect)

Redirects to `/{defaultLocale}` using `navigateTo()`.

### [lang]/index.vue (Homepage)

Fetches hero posts (via `getHeroPosts`), top posts (via `getTopPosts`), and latest posts (paginated, default limit 10) for the current locale. Shows `HeroSection` tile grid if hero posts exist. Two-column layout below: main column with "Latest Articles" post grid + pagination, sidebar (300px on desktop) with `TopRead` widget. Sidebar stacks below main on mobile.

SEO: Title overridden to "TECH.md" (no template suffix), canonical URL, locale alternates,
Open Graph / Twitter metadata, `CollectionPage` JSON-LD, and breadcrumb structured data.

### [lang]/blog/[slug].vue (Post Detail)

Fetches single post by slug for the current locale. Shows back link, title (h1), `PostMeta`, optional cover image,
rendered HTML content (`v-html` in `.notion-content` div), `TableOfContents` sidebar, and `RelatedPosts` grid at the bottom.

SEO: Title is the post title. Canonical URL, `hreflang` alternates, Open Graph / Twitter
metadata, article-specific meta (`published` / `modified` / tags), `BlogPosting` JSON-LD,
and breadcrumb structured data are emitted server-side.

Layout: Single column on mobile/tablet. Two-column grid (`1fr 240px`) at 1024px+ with
sticky TOC sidebar.

404 handling: `throw createError({ statusCode: 404 })` if post not found.

### [lang]/category/[name].vue and [lang]/tag/[name].vue

Filtered post listings with breadcrumb navigation. Same grid and pagination as homepage.
All API calls include the current locale. Each page emits collection-style canonical metadata,
social metadata, and structured data.

### [lang]/about-blog.vue and [lang]/about-me.vue

Static pages fetched from `/api/pages/about-blog?lang={lang}` and `/api/pages/about-me?lang={lang}`.
Render title + HTML content. 404 if not found. Canonical URL, locale alternates, social metadata,
and `AboutPage` structured data are emitted with fallback descriptions summarized from rendered HTML.

## Composable: useApi.ts

Central API client. Uses `useRuntimeConfig()` to determine base URL:
- Server-side: `config.backendUrl` (`http://backend:8000`)
- Client-side: `config.public.backendUrl` (`http://localhost:8000` or `/api` in prod)

**Exported functions**:

| Function | Endpoint | Returns |
|----------|----------|---------|
| `getPosts(lang, opts?)` | `GET /api/posts?lang={lang}` | `PostList` |
| `getFeaturedPosts(lang, limit?)` | `GET /api/posts?lang={lang}&featured=true` | `PostList` |
| `getPost(lang, slug)` | `GET /api/posts/{slug}?lang={lang}` | `Post` |
| `getCategories(lang)` | `GET /api/categories?lang={lang}` | `string[]` |
| `getTags(lang)` | `GET /api/tags?lang={lang}` | `string[]` |
| `getHeroPosts(lang)` | `GET /api/posts/hero?lang={lang}` | `Post[]` |
| `getTopPosts(lang)` | `GET /api/posts/top?lang={lang}` | `Post[]` |
| `getPage(lang, slug)` | `GET /api/pages/{slug}?lang={lang}` | `StaticPage` |

Uses Nuxt's `$fetch` utility internally.

## TypeScript Interfaces (`types/blog.ts`)

```typescript
interface Post {
    id: string; slug: string; title: string; excerpt: string;
    category: string | null; tags: string[];
    published_date: string | null; cover_image: string | null;
    social_image?: string | null;
    author: string; featured?: boolean; language: string;
    hero_position?: number | null; top?: boolean;
    translation_key?: string | null; meta_description?: string | null;
    last_edited_time?: string | null; alternates?: Record<string, string>;
    reading_time?: number; content_html?: string;
    table_of_contents?: TocEntry[]; related_posts?: Post[];
}

interface TocEntry {
    id: string; text: string; level: number;  // 2 or 3
}

interface PostList {
    posts: Post[]; total: number; page: number; has_more: boolean;
}

interface StaticPage {
    id: string; slug: string; title: string; language: string;
    meta_description?: string | null; social_image?: string | null;
    translation_key?: string | null; last_edited_time?: string | null;
    alternates?: Record<string, string>; content_html: string;
}
```

## Theme System

### Architecture

Themes are directories under `frontend/assets/themes/`. Each contains a `theme.css` file
that defines CSS custom properties on `:root`. The theme is selected at **build time** via
the `NUXT_THEME` environment variable (default: `tech-dark`).

### Design Tokens

Both themes define identical token names. All components use these tokens — never hardcode
colors (except in HeroCarousel where white-on-dark-overlay is intentional).

**Color tokens**:
- `--background-color` — Page background
- `--surface-color` — Card/surface background
- `--border-color` — Borders
- `--font-color` — Primary text
- `--font-color-muted` — Secondary/dimmed text
- `--a-color` — Links, CTAs, accent elements
- `--a-color-hover` — Link hover state

**Spacing** (8px base unit):
`--space-xs` (8px), `--space-sm` (16px), `--space-md` (24px), `--space-lg` (32px),
`--space-xl` (48px), `--space-2xl` (64px)

**Typography**:
- `--font-family`: `"Atkinson Hyperlegible Mono", monospace`
- Sizes: `--font-size-xs` (0.75rem) through `--font-size-4xl` (2.5rem)
- Line heights: `--line-height-tight` (1.25), `--line-height-base` (1.5), `--line-height-relaxed` (1.625)

**Transitions**:
- `--transition-fast`: 150ms ease
- `--transition-base`: 250ms cubic-bezier(0.4, 0.0, 0.2, 1)

**Layout**:
- `--touch-target-min`: 48px (accessibility)
- Containers: `--container-sm` (640px) through `--container-xl` (1200px)

### Adding a New Theme

1. Create `frontend/assets/themes/{name}/theme.css`
2. Define all CSS custom properties listed above on `:root`
3. Set `NUXT_THEME={name}` in `.env`
4. Rebuild the frontend (`make dev-rebuild` or redeploy)

## CSS Conventions

See `docs/coding-standards.md` for the full CSS conventions reference (theme tokens, class
naming, responsive breakpoints, accessibility, scoped vs global, and Notion content styling).

### Notion Content Styling

`notion-content.css` styles all HTML generated by the backend renderer. Scoped under
`.notion-content` class. Covers paragraphs, headings, lists, code blocks, blockquotes,
callouts, tables, images, embeds, equations, toggles, and all text annotations.

Prose width limited to `var(--container-md)` (768px) at desktop size.

## Server Routes

### RSS Feed (`/rss.xml`)

Fetches up to 50 posts from the backend for the requested locale (via `?lang=` query param).
Generates RSS 2.0 XML with CDATA, `<language>` tag set to the locale code.
Channel title: "TECH.md". Content-Type: `application/rss+xml; charset=utf-8`.

### Sitemap (`/sitemap.xml`)

Generates URLs for all locales. Static pages and translated posts include `xhtml:link`
hreflang alternates when translation mappings exist. Uses backend `last_edited_time` with
published date fallback for `lastmod`. Priorities: homepage 1.0, about-blog 0.7,
about-me 0.6, posts 0.8.
Content-Type: `application/xml; charset=utf-8`.

### Robots (`/robots.txt`)

Generated at runtime from `siteUrl` so the sitemap reference stays aligned across local,
staging, and production environments.

## Date Formatting

All dates displayed using locale-aware formatting:
```typescript
new Date(date).toLocaleDateString(locale.value, { year: 'numeric', month: 'long', day: 'numeric' })
```

The `locale.value` comes from `useI18n()` and matches the current URL prefix locale code.

## Dockerfile

Three-stage build:
1. **deps**: Install npm dependencies
2. **builder**: Build Nuxt app (receives `NUXT_THEME` build arg)
3. **runtime**: `node:20-alpine`, runs `.output/server/index.mjs` on port 3000

Dev uses `docker-entrypoint.dev.sh` which runs `npm install` before starting the dev server
(needed because volume mounts wipe node_modules).
