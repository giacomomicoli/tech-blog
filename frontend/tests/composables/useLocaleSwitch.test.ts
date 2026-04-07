import { describe, expect, it } from 'vitest'

import { getLocaleSwitchHref, resolveLocaleSwitchPath, stripLocalePrefix } from '~/composables/useLocaleSwitch'

describe('useLocaleSwitch', () => {
  const localePath = (route: string, locale = 'it') => route === '/' ? `/${locale}` : `/${locale}${route}`

  describe('stripLocalePrefix', () => {
    it('strips locale from root paths', () => {
      expect(stripLocalePrefix('/it')).toBe('/')
      expect(stripLocalePrefix('/en')).toBe('/')
    })

    it('strips locale from nested paths', () => {
      expect(stripLocalePrefix('/it/about-blog')).toBe('/about-blog')
      expect(stripLocalePrefix('/en/blog/test-post')).toBe('/blog/test-post')
    })
  })

  describe('getLocaleSwitchHref', () => {
    it('keeps static pages on the same path', () => {
      expect(getLocaleSwitchHref('/it/about-blog', 'en', localePath)).toBe('/en/about-blog')
    })

    it('falls back to locale home for dynamic blog routes', () => {
      expect(getLocaleSwitchHref('/it/blog/test-post', 'en', localePath)).toBe('/en')
    })

    it('falls back to locale home for dynamic taxonomy routes', () => {
      expect(getLocaleSwitchHref('/it/category/News', 'en', localePath)).toBe('/en')
      expect(getLocaleSwitchHref('/it/tag/python', 'en', localePath)).toBe('/en')
    })
  })

  describe('resolveLocaleSwitchPath', () => {
    it('falls back to locale home for blog routes with a slug param', async () => {
      await expect(resolveLocaleSwitchPath({
        currentPath: '/it/blog/test-post',
        routeParams: { slug: 'test-post' },
        sameRoutePath: '/en/blog/test-post',
        fallbackPath: '/en',
        targetLocale: 'en',
      })).resolves.toBe('/en')
    })

    it('falls back to locale home for category and tag routes with params', async () => {
      await expect(resolveLocaleSwitchPath({
        currentPath: '/it/category/News',
        routeParams: { name: 'News' },
        sameRoutePath: '/en/category/News',
        fallbackPath: '/en',
        targetLocale: 'en',
      })).resolves.toBe('/en')

      await expect(resolveLocaleSwitchPath({
        currentPath: '/it/tag/python',
        routeParams: { name: 'python' },
        sameRoutePath: '/en/tag/python',
        fallbackPath: '/en',
        targetLocale: 'en',
      })).resolves.toBe('/en')
    })

    it('keeps static routes untouched', async () => {
      await expect(resolveLocaleSwitchPath({
        currentPath: '/it/about-me',
        routeParams: {},
        sameRoutePath: '/en/about-me',
        fallbackPath: '/en',
        targetLocale: 'en',
      })).resolves.toBe('/en/about-me')
    })

    it('uses explicit alternates when available', async () => {
      await expect(resolveLocaleSwitchPath({
        currentPath: '/it/blog/test-post',
        routeParams: { slug: 'test-post' },
        sameRoutePath: '/en/blog/test-post',
        fallbackPath: '/en',
        targetLocale: 'en',
        alternates: {
          it: '/it/blog/test-post',
          en: '/en/blog/translated-post',
        },
      })).resolves.toBe('/en/blog/translated-post')
    })
  })
})
