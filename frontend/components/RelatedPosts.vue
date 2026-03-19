<script setup lang="ts">
import type { Post } from '~/types/blog'

defineProps<{ posts: Post[] }>()

const { t } = useI18n()
</script>

<template>
  <section v-if="posts.length" class="related-posts">
    <h2 class="related-posts__heading">{{ t('post.relatedPosts') }}</h2>
    <div class="related-posts__grid">
      <PostCard v-for="post in posts" :key="post.id" :post="post" />
    </div>
  </section>
</template>

<style scoped>
.related-posts {
  margin-top: var(--space-2xl);
  padding-top: var(--space-xl);
  border-top: 1px solid var(--border-color);
}

.related-posts__heading {
  font-size: var(--font-size-xl);
  margin: 0 0 var(--space-lg);
}

.related-posts__grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-sm);
}

@media screen and (min-width: 768px) {
  .related-posts__grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media screen and (min-width: 1024px) {
  .related-posts__grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* Force vertical card layout inside the narrower grid cells */
.related-posts__grid :deep(.post-card) {
  flex-direction: column;
}

.related-posts__grid :deep(.post-card__cover) {
  width: 100%;
  aspect-ratio: 16 / 9;
}

.related-posts__grid :deep(.post-card__title) {
  font-size: var(--font-size-base);
}

.related-posts__grid :deep(.post-card__excerpt) {
  -webkit-line-clamp: 3;
}
</style>
