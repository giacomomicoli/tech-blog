<script setup lang="ts">
interface TwitterWidgets {
  widgets?: {
    load: (element?: Element | null) => void
  }
  ready?: (callback: (twttr: TwitterWidgets) => void) => void
  _e?: Array<(twttr: TwitterWidgets) => void>
}

interface TwitterWindow extends Window {
  twttr?: TwitterWidgets
}

definePageMeta({
  key: route => route.path,
})

const route = useRoute()
const { locale, t } = useI18n()
const localePath = useLocalePath()
const slug = computed(() => route.params.slug as string)
const { getPost } = useApi()
const {
  applySeo,
  addStructuredData,
  buildBlogPostingSchema,
  buildBreadcrumbSchema,
  defaultSocialImage,
  siteName,
} = useSeo()
const contentEl = ref<HTMLElement | null>(null)
const interactiveTweetsEnabled = ref(false)
const interactiveTweetsLoading = ref(false)
const interactiveTweetsError = ref('')
const contentRenderKey = ref(0)

const { data: post, error } = await useAsyncData(
  `post-${locale.value}-${slug.value}`,
  () => getPost(locale.value, slug.value),
  { watch: [locale, slug] },
)

if (error.value) {
  throw createError({ statusCode: 404, statusMessage: t('post.notFound') })
}

const postPath = computed(() => `/${locale.value}/blog/${slug.value}`)
const postImage = computed(() => post.value?.social_image || post.value?.cover_image || defaultSocialImage)
const postDescription = computed(() => post.value?.meta_description || post.value?.excerpt)
const postAlternates = computed(() => {
  const alternates = post.value?.alternates || {}

  return Object.fromEntries(
    Object.entries(alternates).map(([lang, alternateSlug]) => [lang, `/${lang}/blog/${alternateSlug}`]),
  )
})

applySeo(() => ({
  title: post.value?.title || siteName,
  description: postDescription.value,
  path: postPath.value,
  image: postImage.value,
  imageAlt: post.value?.title,
  type: 'article',
  alternates: Object.keys(postAlternates.value).length ? postAlternates.value : undefined,
  publishedTime: post.value?.published_date,
  modifiedTime: post.value?.last_edited_time || post.value?.published_date,
  tags: post.value?.tags,
}))

addStructuredData(() => ([
  buildBlogPostingSchema({
    title: post.value?.title || siteName,
    description: postDescription.value,
    path: postPath.value,
    image: postImage.value,
    author: post.value?.author,
    publishedTime: post.value?.published_date,
    modifiedTime: post.value?.last_edited_time || post.value?.published_date,
    category: post.value?.category,
    tags: post.value?.tags,
  }),
  buildBreadcrumbSchema([
    { name: siteName, path: `/${locale.value}` },
    { name: post.value?.category || t('category.breadcrumb'), path: `/${locale.value}` },
    { name: post.value?.title || siteName, path: postPath.value },
  ]),
]), 'blog-post')

const hasTweetEmbeds = computed(() => post.value?.content_html?.includes('twitter-tweet') ?? false)

function getTwitterWidgets() {
  const w = window as TwitterWindow

  if (w.twttr?.widgets) {
    return Promise.resolve(w.twttr)
  }

  if (!w.twttr) {
    w.twttr = {
      _e: [],
      ready(callback) {
        this._e?.push(callback)
      },
    }
  }

  return new Promise<TwitterWidgets>((resolve, reject) => {
    const timeoutId = window.setTimeout(() => {
      reject(new Error('Twitter widgets timed out'))
    }, 8000)

    const finish = (widgets: TwitterWidgets) => {
      window.clearTimeout(timeoutId)
      resolve(widgets)
    }

    const fail = () => {
      window.clearTimeout(timeoutId)
      reject(new Error('Twitter widgets failed to load'))
    }

    w.twttr?.ready?.(finish)

    let script = document.querySelector<HTMLScriptElement>('script[data-twitter-widgets="true"]')
    if (!script) {
      script = document.createElement('script')
      script.src = 'https://platform.twitter.com/widgets.js'
      script.async = true
      script.charset = 'utf-8'
      script.dataset.twitterWidgets = 'true'
      document.head.appendChild(script)
    }

    script.addEventListener('error', fail, { once: true })
  })
}

async function toggleInteractiveTweets() {
  if (!hasTweetEmbeds.value) return

  interactiveTweetsError.value = ''

  if (interactiveTweetsEnabled.value) {
    interactiveTweetsEnabled.value = false
    contentRenderKey.value += 1
    return
  }

  interactiveTweetsEnabled.value = true
  interactiveTweetsLoading.value = true
  contentRenderKey.value += 1

  try {
    await nextTick()
    const twttr = await getTwitterWidgets()
    twttr.widgets?.load(contentEl.value)
  }
  catch {
    interactiveTweetsEnabled.value = false
    interactiveTweetsError.value = t('post.tweetEmbedsBlocked')
    contentRenderKey.value += 1
  }
  finally {
    interactiveTweetsLoading.value = false
  }
}
</script>

<template>
  <article class="post-page">
    <template v-if="post">
      <NuxtLink :to="localePath('/')" class="backhome">{{ t('post.backToBlog') }}</NuxtLink>

      <header class="post-header">
        <h1 class="post-title">{{ post.title }}</h1>
        <PostMeta :post="post" />
      </header>

      <figure v-if="post.cover_image" class="post-hero">
        <img :src="post.cover_image" :alt="post.title" />
      </figure>

      <section v-if="hasTweetEmbeds" class="embed-controls" aria-label="Interactive tweet embeds">
        <div>
          <h2 class="embed-controls__title">{{ t('post.tweetEmbedsTitle') }}</h2>
          <p class="embed-controls__description">{{ t('post.tweetEmbedsDescription') }}</p>
          <p v-if="interactiveTweetsError" class="embed-controls__error">{{ interactiveTweetsError }}</p>
        </div>
        <button
          type="button"
          class="embed-controls__toggle"
          :aria-pressed="interactiveTweetsEnabled"
          :disabled="interactiveTweetsLoading"
          @click="toggleInteractiveTweets"
        >
          {{
            interactiveTweetsLoading
              ? t('post.tweetEmbedsLoading')
              : interactiveTweetsEnabled
                ? t('post.tweetEmbedsDisable')
                : t('post.tweetEmbedsEnable')
          }}
        </button>
      </section>

      <div class="post-layout">
        <div ref="contentEl" :key="contentRenderKey" class="notion-content" v-html="post.content_html" />
        <aside v-if="post.table_of_contents && post.table_of_contents.length > 0" class="post-sidebar">
          <TableOfContents :entries="post.table_of_contents" />
        </aside>
      </div>

      <RelatedPosts v-if="post.related_posts?.length" :posts="post.related_posts" />
    </template>
  </article>
</template>

<style scoped>
.post-page {
  max-width: var(--container-xl);
}

.backhome {
  display: inline-flex;
  align-items: center;
  min-height: var(--touch-target-min);
  font-size: var(--font-size-base);
  margin-block: var(--space-sm);
  padding: var(--space-xs) 0;
}

.post-header {
  margin-block-end: var(--space-md);
}

.post-title {
  font-size: var(--font-size-2xl);
  margin-block-end: var(--space-sm);
  word-wrap: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
}

.post-hero {
  margin: var(--space-md) 0;
  padding: 0;
}

.post-hero img {
  display: block;
  width: 100%;
  height: auto;
  border-radius: var(--space-xs);
  object-fit: cover;
  max-height: 300px;
}

.post-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-lg);
}

.embed-controls {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
  margin: 0 0 var(--space-lg);
  padding: var(--space-md);
  border: 1px solid var(--border-color);
  border-radius: var(--space-xs);
  background: var(--surface-color);
}

.embed-controls__title {
  margin: 0 0 var(--space-xs);
  font-size: var(--font-size-lg);
}

.embed-controls__description,
.embed-controls__error {
  margin: 0;
  font-size: var(--font-size-sm);
  color: var(--font-color-muted);
}

.embed-controls__error {
  color: var(--danger-color, #c75050);
}

.embed-controls__toggle {
  align-self: flex-start;
  min-height: var(--touch-target-min);
  padding: var(--space-xs) var(--space-md);
  border: 1px solid var(--border-color);
  border-radius: var(--space-xs);
  background: var(--background-color);
  color: var(--font-color);
  font: inherit;
  cursor: pointer;
  transition: border-color var(--transition-fast), color var(--transition-fast), background-color var(--transition-fast);
}

.embed-controls__toggle:hover:not(:disabled) {
  border-color: var(--a-color);
  color: var(--a-color);
}

.embed-controls__toggle:disabled {
  opacity: 0.65;
  cursor: wait;
}

.post-sidebar {
  display: none;
}

@media screen and (min-width: 768px) {
  .post-title {
    font-size: var(--font-size-3xl);
  }

  .post-hero img {
    max-height: 400px;
  }

  .embed-controls {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }

  .embed-controls__toggle {
    flex-shrink: 0;
  }
}

@media screen and (min-width: 1024px) {
  .post-title {
    font-size: var(--font-size-4xl);
  }

  .post-hero img {
    max-height: 500px;
  }

  .post-layout {
    grid-template-columns: 1fr 240px;
  }

  .post-sidebar {
    display: block;
  }
}
</style>
