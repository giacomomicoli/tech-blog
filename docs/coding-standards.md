# Coding Standards & Conventions

> Authoritative reference for AI agents and developers. This document defines the coding
> standards, naming conventions, and patterns used throughout the project. All new code
> MUST follow these conventions to maintain consistency.

## General Principles

1. **Keep it simple** — No over-engineering. No abstractions for single-use patterns.
2. **Consistency over preference** — Match existing patterns, even if you'd do it differently.
3. **Don't add what wasn't asked for** — No unsolicited refactoring, comments, docstrings, or features.
4. **Async everywhere (backend)** — All I/O operations use async/await. No blocking calls.
5. **Theme tokens everywhere (frontend)** — Never hardcode colors in components. Use CSS custom properties.

## Python (Backend)

### Style

- **Python version**: 3.12+ (use `str | None` not `Optional[str]`, etc.)
- **Line length**: 100 characters
- **Formatter**: ruff format
- **Linter**: ruff check
- **Quotes**: Double quotes for strings
- **Imports**: stdlib → third-party → local (enforced by ruff/isort)

### Naming

| Element | Convention | Example |
|---------|-----------|---------|
| Functions | `snake_case` | `get_post`, `cache_invalidate` |
| Private helpers | `_snake_case` (leading underscore) | `_get_plain_text`, `_render_heading` |
| Classes | `PascalCase` | `NotionClient`, `Settings` |
| Constants | `UPPER_SNAKE_CASE` | `PREFIX`, `MAX_RETRIES`, `BASE_URL` |
| Module-level singletons | `snake_case` | `notion_client`, `settings` |
| Dict keys (API responses) | `snake_case` | `content_html`, `reading_time`, `cover_image` |

### Module Organization

```python
"""Module docstring."""

# stdlib imports
import asyncio

# third-party imports
from fastapi import APIRouter

# local imports
from src.config import settings
```

Single blank line between import groups. No blank lines within a group.

### Error Handling

- **Notion API errors**: Catch specific exceptions (`NotionNotFound`, `NotionRateLimited`),
  convert to `HTTPException` with appropriate status codes and descriptive detail strings.
- **Missing config**: Return 404 with `"not configured"` detail (not 500).
- **Background tasks**: Catch all exceptions, log them, continue the loop. Never crash.
- **Never expose internal details** in error responses — use generic messages.

### Async Patterns

```python
# Singleton with lazy init
_redis: aioredis.Redis | None = None

async def get_redis() -> aioredis.Redis:
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(...)
    return _redis

# Async generator for paginated results
async def query_database(self, ...) -> AsyncGenerator[dict, None]:
    async for page in self._paginate(...):
        yield page

# Consuming async generators
page_obj = None
async for result in notion_client.query_database(filter=db_filter):
    page_obj = result
    break  # Take first result only
```

### API Response Shapes

All API responses are plain dicts (not Pydantic models). Keep response shapes flat where
possible. Use `snake_case` for all keys.

> For the full response shape of each endpoint, see [`backend-architecture.md`](backend-architecture.md) § API Endpoints.

### Cache Key Patterns

All cache keys use the `blog:` prefix followed by language, type, and identifier.
When adding new cached endpoints, follow this pattern: `blog:{lang}:{type}:{identifier}`.

> For the full key pattern table (with helper functions and examples), see [`backend-architecture.md`](backend-architecture.md) § Cache Layer.

## TypeScript / Vue (Frontend)

### Style

- **TypeScript**: Strict mode, explicit typing on component props and composable return types
- **Vue**: Composition API with `<script setup lang="ts">` (never Options API)
- **Templates**: Single-file components (.vue) with `<template>`, `<script setup>`, `<style scoped>`

### Naming

| Element | Convention | Example |
|---------|-----------|---------|
| Components | `PascalCase.vue` | `PostCard.vue`, `NavBar.vue` |
| Pages | `kebab-case.vue` or `[param].vue` | `index.vue`, `[slug].vue` |
| Composables | `camelCase` with `use` prefix | `useApi.ts` |
| Types/Interfaces | `PascalCase` | `Post`, `TocEntry`, `PostList` |
| CSS classes | `kebab-case` (BEM-inspired) | `.post-preview-cover`, `.navbar-menu` |
| Refs | `camelCase` | `menuOpen`, `currentIndex`, `trackRef` |
| Functions | `camelCase` | `getPosts`, `toggleMenu`, `closeMenu` |
| Event handlers | `camelCase` with descriptive name | `handleScroll`, `goToSlide` |

### Component Structure

```vue
<template>
    <!-- Template content -->
</template>

<script setup lang="ts">
// 1. Imports
import type { Post } from '~/types/blog'

// 2. Props / Emits
const props = defineProps<{ post: Post }>()

// 3. Composables / data fetching
const { getCategories } = useApi()

// 4. Reactive state
const menuOpen = ref(false)

// 5. Computed properties
const formattedDate = computed(() => ...)

// 6. Functions
function toggleMenu() { ... }

// 7. Lifecycle hooks
onMounted(() => { ... })
onUnmounted(() => { ... })
</script>

<style scoped>
/* Component styles using theme tokens */
</style>
```

### Data Fetching

Always use `useAsyncData` for page-level data fetching. Use the composable's functions
(not raw `$fetch`) for type safety. Pass the current `locale` as the first argument.

```typescript
const { locale } = useI18n()
const { getPosts, getCategories } = useApi()

const { data, status } = await useAsyncData(`posts-${locale.value}`, () => getPosts(locale.value, { page: page.value }), {
    watch: [page],
})
```

Cache keys for `useAsyncData` should be descriptive, unique, and include the locale:
- `'posts-{locale}'` — homepage post list
- `'post-{locale}-{slug}'` — individual post
- `'category-{locale}-{name}'` — category page posts
- `'tag-{locale}-{name}'` — tag page posts
- `'featured-posts-{locale}'` — hero carousel data
- `'nav-categories-{locale}'` — navbar categories dropdown

### SEO / Meta

```typescript
// Homepage: override template to show bare title
useHead({ title: 'TECH.md', titleTemplate: '' })

// Subpages: just set title (template adds " | TECH.md")
useHead({ title: post.value?.title })

// Post pages: full OG/Twitter meta
useSeoMeta({
    description: post.value?.excerpt,
    ogTitle: `${post.value.title} | TECH.md`,
    ogDescription: post.value?.excerpt,
    ogImage: post.value?.cover_image,
    ogType: 'article',
    twitterCard: 'summary_large_image',
})
```

### Error Handling

```typescript
// 404 for missing content
if (error.value) {
    throw createError({ statusCode: 404, statusMessage: 'Post not found' })
}
```

## CSS Conventions

### Custom Properties (Theme Tokens)

**Always use theme tokens** for colors, spacing, typography, and transitions. The only
exception is the HeroCarousel where white text on dark overlay is hardcoded intentionally.

```css
/* Correct */
color: var(--font-color);
background-color: var(--surface-color);
padding: var(--space-md);
transition: color var(--transition-fast);

/* Wrong — never do this */
color: #333;
background-color: white;
padding: 24px;
transition: color 0.15s ease;
```

### Class Naming

BEM-inspired with `.block-element` pattern:

```css
.post-preview { }           /* Block */
.post-preview-cover { }     /* Element */
.post-preview-body { }      /* Element */
.post-preview-tags { }      /* Element */
```

No BEM modifiers (no `--modifier`). Use Vue's `:class` binding or data attributes for state.

### Responsive Design

Mobile-first. Use these breakpoints consistently:

```css
/* Mobile: default styles (no media query) */

@media (min-width: 768px) {
    /* Tablet */
}

@media (min-width: 1024px) {
    /* Desktop */
}

@media (min-width: 1200px) {
    /* Large desktop (or 1280px for wider layouts) */
}
```

### Accessibility

- Touch targets: minimum `var(--touch-target-min)` (48px)
- Focus styles: `outline: 2px solid var(--a-color); outline-offset: 2px`
- Reduced motion: wrap animations in `@media (prefers-reduced-motion: no-preference)`
- High contrast: provide `@media (prefers-contrast: high)` overrides where needed
- Print styles: black on white, hide navigation

### Scoped vs Global

- Component styles: Always `<style scoped>` (never leak to other components)
- Global styles: Only in `main.css`, `notion-content.css`, and theme files
- Notion content styles: Scoped under `.notion-content` class in `notion-content.css`

## API Contract

The frontend and backend communicate via a fixed JSON contract. When modifying endpoints,
maintain backward compatibility.

> For the complete response shapes of all endpoints, see [`backend-architecture.md`](backend-architecture.md) § API Endpoints.

## i18n Conventions

### Backend

- All API endpoints accept a `lang` query parameter (validated against `settings.parsed_locales`, falls back to `default_locale`)
- All Notion queries include a `Language` filter matching the requested locale
- All cache keys include the language code as the second segment: `blog:{lang}:...`
- The `_validate_lang()` helper silently falls back — never returns 400 for invalid locale

### Frontend

- Use `const { locale, t } = useI18n()` in components to access locale and translations
- All internal links must be locale-prefixed: `/${locale}/blog/${slug}`, `/${locale}/category/${name}`
- All user-visible static text must use `$t('key')` or `t('key')` — no hardcoded strings
- Locale files are in `frontend/locales/{code}.json` — add new keys to all locale files when adding UI text
- Date formatting uses `locale.value` for locale-aware output
- `useAsyncData` keys must include the locale to avoid stale data across locale switches

## Git & Commit Conventions

- Never commit `.env` files or secrets
- Never commit `node_modules/`, `__pycache__/`, `.nuxt/`, `.output/`
- Prefer specific file staging over `git add -A`
- Write descriptive commit messages focusing on "why" not "what"

## File Organization Rules

- **Backend**: All source code in `backend/src/`. Tests in `backend/tests/`.
- **Frontend**: Follow Nuxt conventions — `pages/`, `components/`, `composables/`, `layouts/`.
- **Docker**: All Docker files in `docker/`. Dockerfiles stay in their service directories.
- **Documentation**: All docs in `docs/`. Keep under 500 lines each.
- **Don't create new files** unless absolutely necessary. Prefer editing existing files.
- **Don't create README.md** files unless explicitly requested.
