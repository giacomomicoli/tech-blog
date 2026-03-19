<script setup lang="ts">
definePageMeta({
  key: route => route.fullPath,
})

const route = useRoute()
const { locale } = useI18n()
const { t } = useI18n()
const localePath = useLocalePath()
const category = route.params.name as string
const { getPosts } = useApi()
const page = ref(1)

const { data, status } = await useAsyncData(
  `category-${route.fullPath}`,
  () => getPosts(locale.value, { category, page: page.value }),
  { watch: [page] },
)

useHead({ title: category })
</script>

<template>
  <div>
    <nav class="breadcrumb">
      <NuxtLink :to="localePath('/')">{{ t('category.breadcrumb') }}</NuxtLink> / <span>{{ category }}</span>
    </nav>
    <h1 class="page-title">{{ category }}</h1>

    <div v-if="status === 'pending'" class="loading">{{ t('category.loading') }}</div>

    <div v-else-if="data && data.posts.length > 0">
      <div class="post-grid">
        <PostCard v-for="post in data.posts" :key="post.id" :post="post" />
      </div>
    </div>

    <div v-else class="empty">
      <p>{{ t('category.noPosts') }}</p>
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
