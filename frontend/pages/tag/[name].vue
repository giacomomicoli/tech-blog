<script setup lang="ts">
definePageMeta({
  key: route => route.fullPath,
})

const route = useRoute()
const { locale, t } = useI18n()
const localePath = useLocalePath()
const tag = computed(() => route.params.name as string)
const { getPosts } = useApi()
const {
  applySeo,
  addStructuredData,
  buildBreadcrumbSchema,
  buildCollectionPageSchema,
  defaultSocialImage,
  siteName,
} = useSeo()
const page = ref(1)

const { data, status } = await useAsyncData(
  `tag-${locale.value}-${tag.value}`,
  () => getPosts(locale.value, { tag: tag.value, page: page.value }),
  { watch: [page, locale, tag] },
)

const pageTitle = computed(() => `#${tag.value}`)
const pageDescription = computed(() => (
  locale.value === 'it'
    ? `Articoli di TECH.md contrassegnati con il tag ${tag.value}.`
    : `TECH.md articles tagged with ${tag.value}.`
))
const pagePath = computed(() => `/${locale.value}/tag/${tag.value}`)
const pageImage = computed(() => (
  data.value?.posts?.[0]?.social_image
  || data.value?.posts?.[0]?.cover_image
  || defaultSocialImage
))

applySeo(() => ({
  title: pageTitle.value,
  description: pageDescription.value,
  path: pagePath.value,
  image: pageImage.value,
  imageAlt: pageTitle.value,
}))

addStructuredData(() => ([
  buildCollectionPageSchema({
    name: pageTitle.value,
    description: pageDescription.value,
    path: pagePath.value,
    image: pageImage.value,
  }),
  buildBreadcrumbSchema([
    { name: siteName, path: `/${locale.value}` },
    { name: pageTitle.value, path: pagePath.value },
  ]),
]), 'tag')
</script>

<template>
  <div>
    <nav class="breadcrumb">
      <NuxtLink :to="localePath('/')">{{ t('tag.breadcrumb') }}</NuxtLink> / <span>#{{ tag }}</span>
    </nav>
    <h1 class="page-title">#{{ tag }}</h1>

    <div v-if="status === 'pending'" class="loading">{{ t('tag.loading') }}</div>

    <div v-else-if="data && data.posts.length > 0">
      <div class="post-grid">
        <PostCard v-for="post in data.posts" :key="post.id" :post="post" />
      </div>
    </div>

    <div v-else class="empty">
      <p>{{ t('tag.noPosts') }}</p>
    </div>
  </div>
</template>

<style scoped>
.breadcrumb {
  font-size: var(--font-size-sm);
  color: var(--font-color-muted);
  margin-bottom: var(--space-sm);
}

.breadcrumb a {
  color: var(--a-color);
  text-decoration: none;
}

.breadcrumb a:hover {
  color: var(--a-color-hover);
  text-decoration: underline;
}

.page-title {
  margin: 0 0 var(--space-lg);
}

.post-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-sm);
}

@media screen and (min-width: 768px) {
  .post-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.loading,
.empty {
  text-align: center;
  color: var(--font-color-muted);
  padding: var(--space-2xl) 0;
}
</style>
