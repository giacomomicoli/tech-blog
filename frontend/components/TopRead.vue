<script setup lang="ts">
import type { Post } from '~/types/blog'

defineProps<{ posts: Post[] }>()

const { locale, t } = useI18n()
const localePath = useLocalePath()

function formatDate(date: string | null): string {
  if (!date) return ''
  return new Date(date).toLocaleDateString(locale.value, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}
</script>

<template>
  <aside v-if="posts.length" class="top-read">
    <h3 class="top-read__heading">{{ t('home.topRead') }}</h3>
    <ul class="top-read__list">
      <li v-for="post in posts" :key="post.id" class="top-read__item">
        <NuxtLink :to="localePath(`/blog/${post.slug}`)" class="top-read__link">
          <img
            v-if="post.cover_image"
            :src="post.cover_image"
            :alt="post.title"
            class="top-read__thumb"
            loading="lazy"
          />
          <div class="top-read__info">
            <span class="top-read__title">{{ post.title }}</span>
            <time v-if="post.published_date" class="top-read__date">{{ formatDate(post.published_date) }}</time>
          </div>
        </NuxtLink>
      </li>
    </ul>
  </aside>
</template>

<style scoped>
.top-read {
  background: var(--surface-color);
  border: 1px solid var(--border-color);
  border-radius: var(--space-xs);
  padding: var(--space-md);
}

.top-read__heading {
  font-size: var(--font-size-lg);
  margin: 0 0 var(--space-md);
  padding-bottom: var(--space-sm);
  border-bottom: 2px solid var(--a-color);
}

.top-read__list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.top-read__link {
  display: flex;
  gap: var(--space-sm);
  text-decoration: none;
  color: var(--font-color);
  align-items: flex-start;
}

.top-read__link:hover .top-read__title,
.top-read__link:focus .top-read__title {
  color: var(--a-color);
}

.top-read__thumb {
  flex: 0 0 72px;
  width: 72px;
  height: 54px;
  object-fit: cover;
  border-radius: 4px;
}

.top-read__info {
  flex: 1;
  min-width: 0;
}

.top-read__title {
  display: block;
  font-size: var(--font-size-sm);
  font-weight: 600;
  line-height: var(--line-height-tight);
  transition: color var(--transition-fast);
}

.top-read__date {
  display: block;
  font-size: var(--font-size-xs);
  color: var(--font-color-muted);
  margin-top: 2px;
}
</style>
