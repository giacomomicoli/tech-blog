<script setup lang="ts">
definePageMeta({
  key: route => route.fullPath,
})

const route = useRoute()
const { locale, t } = useI18n()
const { getPage } = useApi()
const {
  applySeo,
  addStructuredData,
  buildBreadcrumbSchema,
  buildWebPageSchema,
  defaultSocialImage,
  siteName,
  summarizeHtml,
} = useSeo()

const { data: page, error } = await useAsyncData(
  `page-${locale.value}-about-me`,
  () => getPage(locale.value, 'about-me'),
  { watch: [locale] },
)

if (error.value) {
  throw createError({ statusCode: 404, statusMessage: 'Page not found' })
}

const pagePath = computed(() => `/${locale.value}/about-me`)
const pageDescription = computed(() => page.value?.meta_description || summarizeHtml(page.value?.content_html || ''))
const pageAlternates = computed(() => {
  const alternates = page.value?.alternates || {}

  return Object.fromEntries(
    Object.keys(alternates).map(lang => [lang, `/${lang}/about-me`]),
  )
})

applySeo(() => ({
  title: page.value?.title || t('nav.aboutMe'),
  description: pageDescription.value,
  path: pagePath.value,
  image: page.value?.social_image || defaultSocialImage,
  imageAlt: page.value?.title || t('nav.aboutMe'),
  alternates: Object.keys(pageAlternates.value).length ? pageAlternates.value : undefined,
}))

addStructuredData(() => ([
  buildWebPageSchema({
    type: 'AboutPage',
    name: page.value?.title || t('nav.aboutMe'),
    description: pageDescription.value,
    path: pagePath.value,
    image: page.value?.social_image || defaultSocialImage,
  }),
  buildBreadcrumbSchema([
    { name: siteName, path: `/${locale.value}` },
    { name: page.value?.title || t('nav.aboutMe'), path: pagePath.value },
  ]),
]), 'about-me')
</script>

<template>
  <article v-if="page" class="static-page">
    <header class="page-header">
      <h1>{{ page.title }}</h1>
    </header>
    <div class="notion-content" v-html="page.content_html" />
  </article>
</template>

<style scoped>
.static-page {
  max-width: var(--container-xl);
}

.page-header {
  margin-block-end: var(--space-lg);
}
</style>
