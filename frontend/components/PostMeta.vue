<script setup lang="ts">
import type { Post } from '~/types/blog'

defineProps<{ post: Post }>()

const { locale, t } = useI18n()
const localePath = useLocalePath()

function formatDate(date: string | null): string {
  if (!date) return ''
  return new Date(date).toLocaleDateString(locale.value, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}
</script>

<template>
  <div class="post-meta">
    <div class="post-meta-top">
      <time v-if="post.published_date" :datetime="post.published_date">{{ formatDate(post.published_date) }}</time>
      <span v-if="post.author" class="byline">{{ t('post.by') }} <em>{{ post.author }}</em></span>
      <span v-if="post.reading_time" class="reading-time">&middot; {{ post.reading_time }} {{ t('post.minRead') }}</span>
    </div>
    <div v-if="post.category || post.tags.length" class="post-meta-bottom">
      <NuxtLink v-if="post.category" :to="localePath(`/category/${post.category}`)" class="post-meta-category">
        {{ post.category }}
      </NuxtLink>
      <div v-if="post.tags.length" class="post-meta-tags">
        <NuxtLink v-for="tag in post.tags" :key="tag" :to="localePath(`/tag/${tag}`)" class="tag">{{ tag }}</NuxtLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.post-meta {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  font-size: var(--font-size-sm);
  color: var(--font-color-muted);
  margin-block-start: var(--space-sm);
}

.post-meta-top {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-xs);
}

.post-meta-top time {
  display: block;
}

.byline {
  display: block;
}

.reading-time {
  display: none;
}

.post-meta-bottom {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--space-xs);
}

.post-meta-category {
  color: var(--a-color);
  font-weight: 600;
  text-decoration: none;
  text-transform: uppercase;
  font-size: var(--font-size-xs);
  letter-spacing: 0.05em;
}

.post-meta-category:hover {
  color: var(--a-color-hover);
  text-decoration: underline;
}

.post-meta-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
}

.tag {
  background: var(--background-color);
  color: var(--font-color-muted);
  font-size: var(--font-size-xs);
  padding: 2px var(--space-xs);
  border-radius: 4px;
  text-decoration: none;
  border: 1px solid var(--border-color);
}

.tag:hover {
  color: var(--a-color);
  border-color: var(--a-color);
}

@media screen and (min-width: 768px) {
  .post-meta-top time,
  .post-meta-top .byline {
    display: inline;
  }

  .post-meta-top time::after {
    content: " \00b7 ";
  }

  .reading-time {
    display: inline;
  }
}
</style>
