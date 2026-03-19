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
  <article class="post-card">
    <div v-if="post.cover_image" class="post-card__cover">
      <img
        :src="post.cover_image"
        :alt="post.title"
        class="post-card__image"
        loading="lazy"
      />
    </div>
    <div class="post-card__body">
      <header class="post-card__header">
        <NuxtLink
          v-if="post.category"
          :to="localePath(`/category/${post.category}`)"
          class="post-card__category"
        >{{ post.category }}</NuxtLink>
        <h2 class="post-card__title">
          <NuxtLink :to="localePath(`/blog/${post.slug}`)" class="post-card__title-link">{{ post.title }}</NuxtLink>
        </h2>
        <time v-if="post.published_date" class="post-card__date" :datetime="post.published_date">
          {{ formatDate(post.published_date) }}
          <em v-if="post.author"> {{ t('post.by') }} {{ post.author }}</em>
          <span v-if="post.reading_time"> &middot; {{ post.reading_time }} {{ t('post.minRead') }}</span>
        </time>
      </header>
      <p v-if="post.excerpt" class="post-card__excerpt">{{ post.excerpt }}</p>
      <div v-if="post.tags.length" class="post-card__tags">
        <NuxtLink
          v-for="tag in post.tags"
          :key="tag"
          :to="localePath(`/tag/${tag}`)"
          class="post-card__tag"
        >{{ tag }}</NuxtLink>
      </div>
      <footer class="post-card__footer">
        <span class="post-card__readmore">{{ t('post.readMore') }}</span>
      </footer>
    </div>
  </article>
</template>

<style scoped>
.post-card {
  background-color: var(--surface-color);
  border-radius: var(--space-xs);
  overflow: hidden;
  transition: transform var(--transition-base), box-shadow var(--transition-base);
  position: relative;
  display: flex;
  flex-direction: column;
}

.post-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

/* ── Stretched link: title link expands to cover the full card ── */
.post-card__title-link {
  text-decoration: none;
  color: var(--font-color);
}

.post-card__title-link::after {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 1;
}

/* ── Cover image ── */
.post-card__cover {
  flex-shrink: 0;
  aspect-ratio: 16 / 9;
  overflow: hidden;
}

.post-card__image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-base);
}

.post-card:hover .post-card__image {
  transform: scale(1.03);
}

/* ── Body ── */
.post-card__body {
  display: flex;
  flex-direction: column;
  gap: var(--space-xs);
  padding: var(--space-md);
  flex: 1;
}

.post-card__header {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.post-card__category {
  display: inline-block;
  align-self: flex-start;
  font-size: var(--font-size-xs);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: var(--a-color);
  color: #fff;
  padding: 2px var(--space-xs);
  border-radius: 3px;
  text-decoration: none;
  margin-bottom: 4px;
  transition: background-color var(--transition-fast);
  position: relative;
  z-index: 2;
}

.post-card__category:hover {
  background: var(--a-color-hover);
}

.post-card__title {
  font-size: var(--font-size-base);
  line-height: var(--line-height-tight);
  margin: 0;
  color: var(--font-color);
}

.post-card__date {
  display: block;
  font-size: var(--font-size-xs);
  color: var(--font-color-muted);
}

.post-card__date em {
  font-style: normal;
}

.post-card__excerpt {
  font-size: var(--font-size-sm);
  line-height: var(--line-height-base);
  color: var(--font-color-muted);
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-card__tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.post-card__tag {
  font-size: var(--font-size-xs);
  color: var(--font-color-muted);
  padding: 1px var(--space-xs);
  border-radius: 3px;
  text-decoration: none;
  border: 1px solid var(--border-color);
  transition: border-color var(--transition-fast), color var(--transition-fast);
  position: relative;
  z-index: 2;
}

.post-card__tag:hover {
  color: var(--a-color);
  border-color: var(--a-color);
}

.post-card__footer {
  margin-top: auto;
  padding-top: var(--space-xs);
}

.post-card__readmore {
  display: inline-flex;
  align-items: center;
  min-height: 36px;
  padding: 4px var(--space-sm);
  font-size: var(--font-size-sm);
  font-weight: 600;
  white-space: nowrap;
  background-color: var(--a-color);
  color: var(--background-color);
  border-radius: var(--space-xs);
  transition: background-color var(--transition-base);
}

.post-card:hover .post-card__readmore,
.post-card:focus-within .post-card__readmore {
  background-color: var(--a-color-hover);
}

/* ── Tablet (>=768px): side-by-side layout ── */
@media screen and (min-width: 768px) {
  .post-card {
    flex-direction: row;
  }

  .post-card__cover {
    width: 280px;
    aspect-ratio: auto;
  }

  .post-card__title {
    font-size: var(--font-size-lg);
  }

  .post-card__excerpt {
    -webkit-line-clamp: 2;
  }
}

/* ── Desktop (>=1024px) ── */
@media screen and (min-width: 1024px) {
  .post-card__cover {
    width: 320px;
  }

  .post-card__title {
    font-size: var(--font-size-lg);
  }
}
</style>
