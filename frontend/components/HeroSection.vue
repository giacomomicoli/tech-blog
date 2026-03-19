<script setup lang="ts">
import type { Post } from '~/types/blog'

defineProps<{ posts: Post[] }>()

const { locale } = useI18n()
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
  <section v-if="posts.length" class="hero-section" aria-label="Hero posts">
    <div class="hero-grid">
      <!-- Large tile (position 1) -->
      <article
        v-if="posts[0]"
        class="hero-tile hero-tile--large"
        :style="posts[0].cover_image ? { backgroundImage: `url(${posts[0].cover_image})` } : undefined"
      >
        <NuxtLink :to="localePath(`/blog/${posts[0].slug}`)" class="hero-tile__link">
          <div class="hero-tile__overlay" />
          <div class="hero-tile__content">
            <span v-if="posts[0].category" class="hero-tile__category">{{ posts[0].category }}</span>
            <h2 class="hero-tile__title">{{ posts[0].title }}</h2>
            <time v-if="posts[0].published_date" class="hero-tile__date">{{ formatDate(posts[0].published_date) }}</time>
          </div>
        </NuxtLink>
      </article>

      <!-- Small tiles (positions 2-5) -->
      <div class="hero-small-grid">
        <article
          v-for="post in posts.slice(1, 5)"
          :key="post.id"
          class="hero-tile hero-tile--small"
          :style="post.cover_image ? { backgroundImage: `url(${post.cover_image})` } : undefined"
        >
          <NuxtLink :to="localePath(`/blog/${post.slug}`)" class="hero-tile__link">
            <div class="hero-tile__overlay" />
            <div class="hero-tile__content">
              <span v-if="post.category" class="hero-tile__category">{{ post.category }}</span>
              <h3 class="hero-tile__title">{{ post.title }}</h3>
            </div>
          </NuxtLink>
        </article>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero-section {
  margin-bottom: var(--space-xl);
}

.hero-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-sm);
}

.hero-tile {
  position: relative;
  background-size: cover;
  background-position: center;
  background-color: var(--surface-color);
  border-radius: var(--space-xs);
  overflow: hidden;
}

.hero-tile__link {
  display: flex;
  align-items: flex-end;
  width: 100%;
  height: 100%;
  text-decoration: none;
  color: #fff;
}

.hero-tile__overlay {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(to top, rgba(0, 0, 0, 0.92) 0%, rgba(0, 0, 0, 0.6) 40%, rgba(0, 0, 0, 0.3) 100%),
    linear-gradient(to bottom, rgba(0, 0, 0, 0.6) 0%, transparent 40%);
  transition: background var(--transition-base);
}

.hero-tile__link:hover .hero-tile__overlay,
.hero-tile__link:focus .hero-tile__overlay {
  background:
    linear-gradient(to top, rgba(0, 0, 0, 0.95) 0%, rgba(0, 0, 0, 0.7) 40%, rgba(0, 0, 0, 0.4) 100%),
    linear-gradient(to bottom, rgba(0, 0, 0, 0.7) 0%, transparent 40%);
}

.hero-tile__content {
  position: relative;
  z-index: 1;
  padding: var(--space-md);
}

.hero-tile__category {
  display: inline-block;
  font-size: var(--font-size-xs);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: var(--a-color);
  color: #fff;
  padding: 2px var(--space-xs);
  border-radius: 3px;
  margin-bottom: var(--space-xs);
}

.hero-tile__title {
  font-size: var(--font-size-base);
  line-height: var(--line-height-tight);
  margin: 0;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.8), 0 2px 8px rgba(0, 0, 0, 0.5);
  display: -webkit-box;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.hero-tile--small .hero-tile__title {
  -webkit-line-clamp: 4;
}

.hero-tile--large .hero-tile__title {
  -webkit-line-clamp: 4;
}

.hero-tile__date {
  display: block;
  font-size: var(--font-size-xs);
  color: rgba(255, 255, 255, 0.7);
  margin-top: var(--space-xs);
}

.hero-tile--large {
  min-height: 280px;
}

.hero-tile--large .hero-tile__title {
  font-size: var(--font-size-lg);
}

.hero-tile--small {
  min-height: 160px;
}

.hero-small-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-sm);
}

/* Tablet */
@media screen and (min-width: 768px) {
  .hero-tile--large {
    min-height: 360px;
  }

  .hero-tile--large .hero-tile__title {
    font-size: var(--font-size-xl);
  }

  .hero-tile--large .hero-tile__content {
    padding: var(--space-lg);
  }

  .hero-small-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .hero-tile--small {
    min-height: 180px;
  }
}

/* Desktop */
@media screen and (min-width: 1024px) {
  .hero-grid {
    grid-template-columns: 3fr 2fr;
    align-items: stretch;
  }

  .hero-tile--large {
    min-height: 420px;
    grid-row: 1;
  }

  .hero-tile--large .hero-tile__title {
    font-size: var(--font-size-2xl);
  }

  .hero-small-grid {
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(2, 1fr);
    height: 100%;
  }

  /* If only 3 small tiles, span the last one across both columns to fill the gap */
  .hero-small-grid .hero-tile--small:last-child:nth-child(3) {
    grid-column: 1 / -1;
  }

  .hero-tile--small {
    min-height: 0;
  }
}
</style>
