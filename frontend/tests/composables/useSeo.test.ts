import { defineComponent } from 'vue'
import { mountSuspended, mockNuxtImport } from '@nuxt/test-utils/runtime'
import { beforeEach, describe, expect, it, vi } from 'vitest'

const { useHeadMock, useSeoMetaMock } = vi.hoisted(() => ({
  useHeadMock: vi.fn(),
  useSeoMetaMock: vi.fn(),
}))

mockNuxtImport('useHead', () => useHeadMock)
mockNuxtImport('useSeoMeta', () => useSeoMetaMock)
mockNuxtImport('useRuntimeConfig', () => () => ({
  public: {
    siteUrl: 'https://tech.example.com',
    defaultLocale: 'it',
    supportedLocales: 'it,en',
  },
}))
mockNuxtImport('useI18n', () => () => ({
  locale: { value: 'it' },
}))

describe('useSeo', () => {
  beforeEach(() => {
    useHeadMock.mockReset()
    useSeoMetaMock.mockReset()
  })

  it('builds canonical and alternate links', async () => {
    const { useSeo } = await import('~/composables/useSeo')

    const Harness = defineComponent({
      setup() {
        const { applySeo } = useSeo()

        applySeo({
          title: 'Post title',
          path: '/it/blog/post-title',
          alternates: {
            it: '/it/blog/post-title',
            en: '/en/blog/post-title',
          },
        })

        return () => null
      },
    })

    await mountSuspended(Harness)

    const headInput = useHeadMock.mock.calls[0][0]()
    expect(headInput.link).toEqual([
      { rel: 'canonical', href: 'https://tech.example.com/it/blog/post-title' },
      { rel: 'alternate', hreflang: 'it', href: 'https://tech.example.com/it/blog/post-title' },
      { rel: 'alternate', hreflang: 'en', href: 'https://tech.example.com/en/blog/post-title' },
      { rel: 'alternate', hreflang: 'x-default', href: 'https://tech.example.com/it/blog/post-title' },
    ])
  })

  it('emits article seo metadata with fallback image resolution', async () => {
    const { useSeo } = await import('~/composables/useSeo')

    const Harness = defineComponent({
      setup() {
        const { applySeo } = useSeo()

        applySeo({
          title: 'Post title',
          description: 'Readable summary',
          path: '/it/blog/post-title',
          type: 'article',
          tags: ['seo', 'nuxt'],
          publishedTime: '2026-02-01',
          modifiedTime: '2026-02-05T10:00:00.000Z',
        })

        return () => null
      },
    })

    await mountSuspended(Harness)

    const seoInput = useSeoMetaMock.mock.calls[0][0]
    expect(seoInput.ogType()).toBe('article')
    expect(seoInput.ogUrl()).toBe('https://tech.example.com/it/blog/post-title')
    expect(seoInput.ogImage()).toBe('https://tech.example.com/social/default-social-card.png')
    expect(seoInput.robots()).toBe('index,follow,max-image-preview:large')
    expect(seoInput.articlePublishedTime()).toBe('2026-02-01')
    expect(seoInput.articleModifiedTime()).toBe('2026-02-05T10:00:00.000Z')
    expect(seoInput.articleTag()).toEqual(['seo', 'nuxt'])
  })

  it('summarizes html conservatively', async () => {
    const { useSeo } = await import('~/composables/useSeo')
    let summary = ''
    const Harness = defineComponent({
      setup() {
        const { summarizeHtml } = useSeo()

        summary = summarizeHtml('<p>Hello <strong>world</strong>.</p><p>Second paragraph.</p>', 20)
        return () => null
      },
    })

    await mountSuspended(Harness)

    expect(summary).toBe('Hello world. Second...')
  })
})
