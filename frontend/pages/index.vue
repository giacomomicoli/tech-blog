<script setup lang="ts">
const { locale, t } = useI18n()
const { getPosts, getHeroPosts, getTopPosts } = useApi()
const {
  applySeo,
  addStructuredData,
  buildBreadcrumbSchema,
  buildCollectionPageSchema,
  defaultSocialImage,
  siteName,
} = useSeo()
const page = ref(1)

const { data, status } = await useAsyncData(`posts-${locale.value}`, () => getPosts(locale.value, { page: page.value }), {
  watch: [page, locale],
})

const { data: heroData } = await useAsyncData(`hero-posts-${locale.value}`, () => getHeroPosts(locale.value), {
  watch: [locale],
})

const { data: topData } = await useAsyncData(`top-posts-${locale.value}`, () => getTopPosts(locale.value), {
  watch: [locale],
})

const pageTitle = siteName
const pageDescription = computed(() => {
  if (heroData.value?.[0]?.meta_description) {
    return heroData.value[0].meta_description
  }

  if (heroData.value?.[0]?.excerpt) {
    return heroData.value[0].excerpt
  }

  return locale.value === 'it'
    ? 'TECH.md raccoglie articoli tecnici, tutorial, riflessioni e contenuti curati dal mondo dello sviluppo software e della cultura digitale.'
    : 'TECH.md gathers technical articles, tutorials, essays, and curated writing about software development and digital culture.'
})
const homepageAlternates = computed(() => ({
  it: '/it',
  en: '/en',
}))
const homepageImage = computed(() => (
  heroData.value?.[0]?.social_image
  || heroData.value?.[0]?.cover_image
  || defaultSocialImage
))

applySeo(() => ({
  title: pageTitle,
  description: pageDescription.value,
  path: `/${locale.value}`,
  image: homepageImage.value,
  imageAlt: pageTitle,
  noTemplate: true,
  alternates: homepageAlternates.value,
}))

addStructuredData(() => ([
  buildCollectionPageSchema({
    name: pageTitle,
    description: pageDescription.value,
    path: `/${locale.value}`,
    image: homepageImage.value,
  }),
  buildBreadcrumbSchema([
    { name: pageTitle, path: `/${locale.value}` },
  ]),
]), 'homepage')

function nextPage() {
  if (data.value?.has_more) page.value++
}

function prevPage() {
  if (page.value > 1) page.value--
}
</script>

<template>
  <div>
    <h1 class="sr-only">{{ pageTitle }}</h1>
    <HeroSection v-if="heroData?.length" :posts="heroData" />

    <div class="content-layout">
      <main class="content-main">
        <h2 class="section-title">{{ t('home.latestPosts') }}</h2>

        <div v-if="status === 'pending'" class="loading">{{ t('home.loading') }}</div>

        <div v-else-if="data && data.posts.length > 0">
          <div class="post-grid">
            <PostCard v-for="post in data.posts" :key="post.id" :post="post" />
          </div>

          <nav v-if="data.total > 10" class="pagination">
            <button :disabled="page <= 1" @click="prevPage">{{ t('pagination.previous') }}</button>
            <span class="pagination-info">{{ t('pagination.page', { page }) }}</span>
            <button :disabled="!data.has_more" @click="nextPage">{{ t('pagination.next') }}</button>
          </nav>
        </div>

        <div v-else class="empty">
          <p>{{ t('home.noPosts') }}</p>
        </div>
      </main>

      <aside v-if="topData?.length" class="content-sidebar">
        <TopRead :posts="topData" />
      </aside>
    </div>
  </div>
</template>

<style scoped>
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

.content-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-lg);
}

.section-title {
  margin: 0 0 var(--space-lg);
}

.post-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-md);
}

@media screen and (min-width: 1200px) {
  .content-layout {
    grid-template-columns: 1fr 300px;
  }
}

.content-sidebar {
  order: -1;
}

@media screen and (min-width: 1200px) {
  .content-sidebar {
    order: 0;
  }
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--space-sm);
  margin-top: var(--space-xl);
}

.pagination button {
  display: inline-flex;
  align-items: center;
  min-height: var(--touch-target-min);
  padding: var(--space-xs) var(--space-sm);
  font-family: var(--font-family);
  font-size: var(--font-size-base);
  font-weight: 600;
  border: none;
  border-radius: var(--space-xs);
  background-color: var(--a-color);
  color: var(--background-color);
  cursor: pointer;
  transition: background-color var(--transition-base);
}

.pagination button:hover:not(:disabled) {
  background-color: var(--a-color-hover);
}

.pagination button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.pagination-info {
  font-size: var(--font-size-sm);
  color: var(--font-color-muted);
}

.loading,
.empty {
  text-align: center;
  color: var(--font-color-muted);
  padding: var(--space-2xl) 0;
}
</style>
