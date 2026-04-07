<script setup lang="ts">
import { getLocaleSwitchHref, resolveLocaleSwitchPath } from '~/composables/useLocaleSwitch'

const route = useRoute()
const { locale, locales, t } = useI18n()
const localePath = useLocalePath()
const switchLocalePath = useSwitchLocalePath()
const { getCategories, getPage, getPost } = useApi()

const categoriesKey = computed(() => `nav-categories-${locale.value}`)
const { data: categories } = await useAsyncData(categoriesKey, () => getCategories(locale.value), {
  watch: [locale],
})

const menuOpen = ref(false)
const dropdownOpen = ref(false)

function toggleMenu() {
  menuOpen.value = !menuOpen.value
  if (!menuOpen.value) dropdownOpen.value = false
}

function closeMenu() {
  menuOpen.value = false
  dropdownOpen.value = false
}

function toggleDropdown() {
  dropdownOpen.value = !dropdownOpen.value
}

const availableLocales = computed(() =>
  (locales.value as Array<{ code: string }>).map(l => l.code).filter(code => code !== locale.value)
)

function shouldHandleLocaleSwitch(event: MouseEvent): boolean {
  return !(event.defaultPrevented || event.button !== 0 || event.metaKey || event.altKey || event.ctrlKey || event.shiftKey)
}

function getLanguageHref(targetLocale: string): string {
  return getLocaleSwitchHref(route.path, targetLocale, localePath)
}

async function switchLanguage(targetLocale: string, event: MouseEvent) {
  if (!shouldHandleLocaleSwitch(event)) return

  event.preventDefault()
  closeMenu()

  let alternates: Record<string, string> | undefined
  const normalizedPath = route.path.replace(/^\/[^/]+(?=\/|$)/, '') || '/'

  if (normalizedPath.startsWith('/blog/')) {
    const slug = typeof route.params.slug === 'string' ? route.params.slug : null
    if (slug) {
      try {
        const post = await getPost(locale.value, slug)
        if (post.alternates && Object.keys(post.alternates).length) {
          alternates = Object.fromEntries(
            Object.entries(post.alternates).map(([lang, alternateSlug]) => [lang, localePath(`/blog/${alternateSlug}`, lang)]),
          )
        }
      }
      catch {
        alternates = undefined
      }
    }
  }

  if (normalizedPath === '/about-blog' || normalizedPath === '/about-me') {
    const pageSlug = normalizedPath.slice(1)
    try {
      const page = await getPage(locale.value, pageSlug)
      if (page.alternates && Object.keys(page.alternates).length) {
        alternates = Object.fromEntries(
          Object.keys(page.alternates).map(lang => [lang, localePath(`/${pageSlug}`, lang)]),
        )
      }
    }
    catch {
      alternates = alternates || undefined
    }
  }

  const destination = await resolveLocaleSwitchPath({
    currentPath: route.path,
    routeParams: route.params as Record<string, string | string[] | undefined>,
    sameRoutePath: switchLocalePath(targetLocale),
    fallbackPath: localePath('/', targetLocale),
    targetLocale,
    alternates,
  })

  await navigateTo(destination)
}
</script>

<template>
  <nav class="navbar" aria-label="Main navigation">
    <NuxtLink :to="localePath('/')" class="navbar-brand" @click="closeMenu">TECH.md</NuxtLink>

    <button
      class="navbar-toggle"
      :aria-expanded="menuOpen"
      aria-controls="navbar-menu"
      aria-label="Toggle navigation menu"
      @click="toggleMenu"
    >
      <span class="hamburger" :class="{ open: menuOpen }" />
    </button>

    <ul id="navbar-menu" class="navbar-menu" :class="{ open: menuOpen }">
      <li>
        <NuxtLink :to="localePath('/')" class="navbar-link" @click="closeMenu">{{ t('nav.home') }}</NuxtLink>
      </li>
      <li
        class="navbar-dropdown"
        @mouseenter="dropdownOpen = true"
        @mouseleave="dropdownOpen = false"
      >
        <button
          class="navbar-link dropdown-trigger"
          :aria-expanded="dropdownOpen"
          @click="toggleDropdown"
        >
          {{ t('nav.categories') }}
          <span class="dropdown-arrow" :class="{ open: dropdownOpen }">&#9662;</span>
        </button>
        <ul v-show="dropdownOpen" class="dropdown-menu">
          <li v-if="!categories?.length" class="dropdown-empty">{{ t('nav.noCategories') }}</li>
          <li v-for="cat in categories" :key="cat">
            <NuxtLink :to="localePath(`/category/${cat}`)" class="dropdown-link" @click="closeMenu">{{ cat }}</NuxtLink>
          </li>
        </ul>
      </li>
      <li>
        <NuxtLink :to="localePath('/about-blog')" class="navbar-link" @click="closeMenu">{{ t('nav.aboutBlog') }}</NuxtLink>
      </li>
      <li>
        <NuxtLink :to="localePath('/about-me')" class="navbar-link" @click="closeMenu">{{ t('nav.aboutMe') }}</NuxtLink>
      </li>
      <li v-for="loc in availableLocales" :key="loc" class="navbar-lang">
        <NuxtLink :to="getLanguageHref(loc)" class="navbar-link navbar-link-lang" :aria-label="t('language.switch')" @click="switchLanguage(loc, $event)">
          {{ loc.toUpperCase() }}
        </NuxtLink>
      </li>
    </ul>
  </nav>
</template>

<style scoped>
.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--space-sm);
}

.navbar-brand {
  font-size: var(--font-size-lg);
  font-weight: 700;
  text-decoration: none;
  color: var(--font-color);
  line-height: var(--line-height-tight);
}

.navbar-brand:hover {
  color: var(--a-color-hover);
}

.navbar-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: var(--touch-target-min);
  height: var(--touch-target-min);
  padding: 0;
  background: none;
  border: 1px solid var(--border-color);
  border-radius: var(--space-xs);
  cursor: pointer;
}

.hamburger,
.hamburger::before,
.hamburger::after {
  display: block;
  width: 20px;
  height: 2px;
  background: var(--font-color);
  border-radius: 1px;
  transition: transform var(--transition-base), opacity var(--transition-base);
  position: relative;
}

.hamburger::before,
.hamburger::after {
  content: '';
  position: absolute;
  left: 0;
  width: 20px;
}

.hamburger::before {
  top: -6px;
}

.hamburger::after {
  top: 6px;
}

.hamburger.open {
  background: transparent;
}

.hamburger.open::before {
  top: 0;
  transform: rotate(45deg);
}

.hamburger.open::after {
  top: 0;
  transform: rotate(-45deg);
}

.navbar-menu {
  display: none;
  list-style: none;
  margin: 0;
  padding: 0;
  flex-direction: column;
  width: 100%;
  gap: 0;
}

.navbar-menu.open {
  display: flex;
}

.navbar-link {
  display: flex;
  align-items: center;
  min-height: var(--touch-target-min);
  padding: var(--space-xs) 0;
  font-size: var(--font-size-base);
  font-weight: 500;
  text-decoration: none;
  color: var(--font-color);
  background: none;
  border: none;
  cursor: pointer;
  font-family: var(--font-family);
  width: 100%;
}

.navbar-link:hover,
.navbar-link:focus {
  color: var(--a-color);
}

.navbar-link.router-link-active {
  color: var(--a-color);
}

.dropdown-trigger {
  gap: var(--space-xs);
}

.dropdown-arrow {
  font-size: var(--font-size-xs);
  transition: transform var(--transition-fast);
}

.dropdown-arrow.open {
  transform: rotate(180deg);
}

.navbar-dropdown {
  position: relative;
}

.dropdown-menu {
  list-style: none;
  margin: 0;
  padding: var(--space-xs) 0;
  padding-left: var(--space-md);
}

.dropdown-link {
  display: flex;
  align-items: center;
  min-height: var(--touch-target-min);
  padding: var(--space-xs) 0;
  font-size: var(--font-size-sm);
  text-decoration: none;
  color: var(--font-color);
}

.dropdown-link:hover,
.dropdown-link:focus {
  color: var(--a-color);
}

.dropdown-empty {
  padding: var(--space-xs) 0;
  font-size: var(--font-size-sm);
  color: var(--font-color-muted);
}

.navbar-link-lang {
  font-weight: 700;
  font-size: var(--font-size-sm);
  letter-spacing: 0.05em;
}

/* ── Desktop ── */
@media screen and (min-width: 768px) {
  .navbar {
    flex-wrap: nowrap;
  }

  .navbar-brand {
    font-size: var(--font-size-xl);
  }

  .navbar-toggle {
    display: none;
  }

  .navbar-menu {
    display: flex;
    flex-direction: row;
    width: auto;
    align-items: center;
    gap: var(--space-xs);
  }

  .navbar-link {
    padding: var(--space-xs) var(--space-sm);
    width: auto;
    white-space: nowrap;
  }

  .dropdown-menu {
    position: absolute;
    top: 100%;
    left: 0;
    min-width: 180px;
    padding: var(--space-xs);
    padding-left: var(--space-xs);
    background: var(--surface-color);
    border: 1px solid var(--border-color);
    border-radius: var(--space-xs);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 100;
  }

  .dropdown-link {
    padding: var(--space-xs) var(--space-sm);
    border-radius: 4px;
  }

  .dropdown-link:hover {
    background: var(--background-color);
  }
}

@media screen and (min-width: 1024px) {
  .navbar-brand {
    font-size: var(--font-size-2xl);
  }
}
</style>
