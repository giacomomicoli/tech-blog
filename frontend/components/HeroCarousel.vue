<script setup lang="ts">
import type { Post } from '~/types/blog'

const props = defineProps<{ posts: Post[] }>()

const { locale, t } = useI18n()
const localePath = useLocalePath()
const currentIndex = ref(0)
const trackRef = ref<HTMLElement | null>(null)
let autoAdvanceTimer: ReturnType<typeof setInterval> | undefined

function goToSlide(index: number) {
  currentIndex.value = index
  trackRef.value?.children[index]?.scrollIntoView({
    behavior: 'smooth',
    block: 'nearest',
    inline: 'start',
  })
}

function nextSlide() {
  goToSlide((currentIndex.value + 1) % props.posts.length)
}

function handleScroll() {
  if (!trackRef.value) return
  const scrollLeft = trackRef.value.scrollLeft
  const slideWidth = trackRef.value.offsetWidth
  currentIndex.value = Math.round(scrollLeft / slideWidth)
}

onMounted(() => {
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (!prefersReducedMotion && props.posts.length > 1) {
    autoAdvanceTimer = setInterval(nextSlide, 6000)
  }
})

onUnmounted(() => {
  if (autoAdvanceTimer) clearInterval(autoAdvanceTimer)
})
</script>

<template>
  <section class="hero" aria-label="Featured posts">
    <div ref="trackRef" class="hero-track" @scroll.passive="handleScroll">
      <article
        v-for="(post, i) in posts"
        :key="post.id"
        class="hero-slide"
        :style="post.cover_image ? { backgroundImage: `url(${post.cover_image})` } : undefined"
        :aria-hidden="i !== currentIndex"
      >
        <div class="hero-overlay" />
        <div class="hero-content">
          <h2 class="hero-title">
            <NuxtLink :to="localePath(`/blog/${post.slug}`)">{{ post.title }}</NuxtLink>
          </h2>
          <p v-if="post.excerpt" class="hero-excerpt">{{ post.excerpt }}</p>
          <NuxtLink :to="localePath(`/blog/${post.slug}`)" class="hero-cta">
            {{ t('post.readMore') }}
          </NuxtLink>
        </div>
      </article>
    </div>

    <nav v-if="posts.length > 1" class="hero-dots" role="tablist" aria-label="Slide navigation">
      <button
        v-for="(post, i) in posts"
        :key="post.id"
        role="tab"
        :aria-selected="i === currentIndex"
        :aria-label="`Go to slide ${i + 1}: ${post.title}`"
        :class="['hero-dot', { active: i === currentIndex }]"
        @click="goToSlide(i)"
      />
    </nav>
  </section>
</template>

<style scoped>
.hero {
  position: relative;
  height: 50vh;
  min-height: 300px;
  max-height: 700px;
  border-radius: var(--space-xs);
  overflow: hidden;
  margin-bottom: var(--space-lg);
}

.hero-track {
  display: flex;
  height: 100%;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.hero-track::-webkit-scrollbar {
  display: none;
}

.hero-slide {
  flex: 0 0 100%;
  scroll-snap-align: start;
  position: relative;
  background-size: cover;
  background-position: center;
  background-color: var(--surface-color);
  display: flex;
  align-items: flex-end;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.75) 0%, rgba(0, 0, 0, 0.2) 50%, transparent 100%);
}

.hero-content {
  position: relative;
  z-index: 1;
  padding: var(--space-lg);
  max-width: 720px;
}

.hero-title {
  font-size: var(--font-size-2xl);
  margin-bottom: var(--space-xs);
  line-height: var(--line-height-tight);
}

.hero-title a {
  color: #fff;
  text-decoration: none;
}

.hero-title a:hover,
.hero-title a:focus {
  text-decoration: underline;
}

.hero-excerpt {
  color: rgba(255, 255, 255, 0.85);
  font-size: var(--font-size-base);
  line-height: var(--line-height-relaxed);
  margin-bottom: var(--space-sm);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.hero-cta {
  display: inline-flex;
  align-items: center;
  min-height: var(--touch-target-min);
  padding: var(--space-xs) var(--space-sm);
  font-size: var(--font-size-base);
  font-weight: 600;
  text-decoration: none;
  white-space: nowrap;
  background-color: var(--a-color);
  color: #fff;
  border-radius: var(--space-xs);
  transition: background-color var(--transition-base);
}

.hero-cta:hover,
.hero-cta:focus {
  background-color: var(--a-color-hover);
  color: #fff;
}

.hero-dots {
  position: absolute;
  bottom: var(--space-sm);
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: var(--space-xs);
  z-index: 2;
}

.hero-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  border: 2px solid rgba(255, 255, 255, 0.7);
  background: transparent;
  cursor: pointer;
  padding: 0;
  transition: background-color var(--transition-fast);
}

.hero-dot.active {
  background: #fff;
  border-color: #fff;
}

.hero-dot:hover {
  background: rgba(255, 255, 255, 0.5);
}

@media screen and (min-width: 768px) {
  .hero {
    height: 70vh;
    min-height: 400px;
  }

  .hero-content {
    padding: var(--space-xl);
  }

  .hero-title {
    font-size: var(--font-size-3xl);
  }

  .hero-excerpt {
    font-size: var(--font-size-md);
  }
}

@media screen and (min-width: 1024px) {
  .hero-content {
    padding: var(--space-2xl);
  }

  .hero-title {
    font-size: var(--font-size-4xl);
  }
}
</style>
