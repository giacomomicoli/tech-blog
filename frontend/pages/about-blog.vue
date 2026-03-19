<script setup lang="ts">
definePageMeta({
  key: route => route.fullPath,
})

const route = useRoute()
const { locale } = useI18n()
const { t } = useI18n()
const { getPage } = useApi()

const { data: page, error } = await useAsyncData(`page-${route.fullPath}`, () => getPage(locale.value, 'about-blog'))

if (error.value) {
  throw createError({ statusCode: 404, statusMessage: 'Page not found' })
}

useHead({ title: page.value?.title || t('nav.aboutBlog') })
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
