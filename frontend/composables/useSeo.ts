import { toValue } from 'vue'
import type { MaybeRefOrGetter } from 'vue'

import type { AlternatesMap } from '~/types/blog'

interface SeoOptions {
  title: string
  description?: string | null
  path: string
  image?: string | null
  imageAlt?: string | null
  type?: 'website' | 'article'
  noTemplate?: boolean
  alternates?: AlternatesMap
  robots?: string
  publishedTime?: string | null
  modifiedTime?: string | null
  tags?: string[]
}

interface BreadcrumbItem {
  name: string
  path: string
}

const SITE_NAME = 'TECH.md'
const SITE_DESCRIPTION = 'TECH.md is a multilingual tech blog powered by Notion, focused on clear writing, practical insights, and curated developer content.'
const DEFAULT_SOCIAL_IMAGE = '/social/default-social-card.png'
const SITE_LOGO = '/apple-touch-icon.png'

function normalizePath(path: string): string {
  if (!path.startsWith('/')) {
    return `/${path}`
  }

  return path === '/' ? path : path.replace(/\/+$/, '')
}

function normalizeSiteUrl(siteUrl: string): string {
  return siteUrl.replace(/\/+$/, '')
}

function toAbsoluteUrl(siteUrl: string, pathOrUrl: string): string {
  if (/^https?:\/\//i.test(pathOrUrl)) {
    return pathOrUrl
  }

  return `${normalizeSiteUrl(siteUrl)}${normalizePath(pathOrUrl)}`
}

function getLocaleCode(locale: string): string {
  const localeMap: Record<string, string> = {
    it: 'it_IT',
    en: 'en_US',
  }

  return localeMap[locale] || locale
}

function getSiteDescription(description?: string | null): string {
  return description?.trim() || SITE_DESCRIPTION
}

function stripHtml(html: string): string {
  return html
    .replace(/<style[\s\S]*?<\/style>/gi, ' ')
    .replace(/<script[\s\S]*?<\/script>/gi, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/\s+/g, ' ')
    .replace(/\s+([.,;:!?])/g, '$1')
    .trim()
}

function hasAlternates(alternates?: AlternatesMap): alternates is AlternatesMap {
  return Boolean(alternates && Object.keys(alternates).length)
}

export function useSeo() {
  const { locale } = useI18n()
  const config = useRuntimeConfig()
  const siteUrl = normalizeSiteUrl(config.public.siteUrl || 'http://localhost:3000')
  const defaultLocale = config.public.defaultLocale || 'it'
  const supportedLocales = (config.public.supportedLocales || 'it,en')
    .split(',')
    .map(code => code.trim())
    .filter(Boolean)

  function resolveCanonical(path: string): string {
    return toAbsoluteUrl(siteUrl, normalizePath(path))
  }

  function resolveImage(image?: string | null): string {
    return toAbsoluteUrl(siteUrl, image || DEFAULT_SOCIAL_IMAGE)
  }

  function buildAlternateLinks(alternates?: AlternatesMap): Array<Record<string, string>> {
    if (!hasAlternates(alternates)) {
      return []
    }

    const links = Object.entries(alternates)
      .filter(([lang]) => supportedLocales.includes(lang))
      .map(([lang, path]) => ({
        rel: 'alternate',
        hreflang: lang,
        href: toAbsoluteUrl(siteUrl, path),
      }))

    const xDefaultPath = alternates[defaultLocale] || alternates[locale.value]
    if (xDefaultPath) {
      links.push({
        rel: 'alternate',
        hreflang: 'x-default',
        href: toAbsoluteUrl(siteUrl, xDefaultPath),
      })
    }

    return links
  }

  function applySeo(options: MaybeRefOrGetter<SeoOptions>): void {
    useHead(() => {
      const resolvedOptions = toValue(options)
      const canonical = resolveCanonical(resolvedOptions.path)
      const headOptions: {
        title: string
        titleTemplate?: string
        htmlAttrs: { lang: string }
        link: Array<Record<string, string>>
      } = {
        title: resolvedOptions.title,
        htmlAttrs: {
          lang: locale.value,
        },
        link: [
          { rel: 'canonical', href: canonical },
          ...buildAlternateLinks(resolvedOptions.alternates),
        ],
      }

      if (resolvedOptions.noTemplate) {
        headOptions.titleTemplate = ''
      }

      return headOptions
    })

    const resolvedOptions = () => toValue(options)
    const description = () => getSiteDescription(resolvedOptions().description)
    const canonical = () => resolveCanonical(resolvedOptions().path)
    const image = () => resolveImage(resolvedOptions().image)
    const title = () => resolvedOptions().title
    const socialTitle = () => resolvedOptions().noTemplate ? title() : `${title()} | ${SITE_NAME}`
    const imageAlt = () => resolvedOptions().imageAlt || title()
    const alternateLocaleCodes = () => {
      const locales = Object.keys(resolvedOptions().alternates || {})
        .filter(lang => lang !== locale.value)
        .map(getLocaleCode)

      return locales.length ? locales : undefined
    }

    useSeoMeta({
      title,
      description,
      robots: () => resolvedOptions().robots || 'index,follow,max-image-preview:large',
      ogTitle: socialTitle,
      ogDescription: description,
      ogUrl: canonical,
      ogType: () => resolvedOptions().type || 'website',
      ogSiteName: SITE_NAME,
      ogLocale: () => getLocaleCode(locale.value),
      ogLocaleAlternate: alternateLocaleCodes,
      ogImage: image,
      ogImageSecureUrl: image,
      ogImageAlt: imageAlt,
      twitterCard: 'summary_large_image',
      twitterTitle: socialTitle,
      twitterDescription: description,
      twitterImage: image,
      twitterImageAlt: imageAlt,
      articlePublishedTime: () => resolvedOptions().publishedTime || undefined,
      articleModifiedTime: () => resolvedOptions().modifiedTime || undefined,
      articleTag: () => resolvedOptions().tags?.length ? resolvedOptions().tags : undefined,
    })
  }

  function addStructuredData(
    schema: MaybeRefOrGetter<Record<string, unknown> | Array<Record<string, unknown>>>,
    key = 'schema',
  ): void {
    useHead(() => ({
      script: [
        {
          key: `seo-schema-${key}`,
          type: 'application/ld+json',
          children: JSON.stringify(toValue(schema)),
        },
      ],
    }))
  }

  function buildWebsiteSchema(): Record<string, unknown> {
    return {
      '@context': 'https://schema.org',
      '@type': 'WebSite',
      name: SITE_NAME,
      description: SITE_DESCRIPTION,
      url: siteUrl,
      inLanguage: supportedLocales,
      publisher: {
        '@type': 'Organization',
        name: SITE_NAME,
        founder: {
          '@type': 'Person',
          name: 'FakeJack',
        },
        logo: {
          '@type': 'ImageObject',
          url: toAbsoluteUrl(siteUrl, SITE_LOGO),
        },
      },
    }
  }

  function buildBreadcrumbSchema(items: BreadcrumbItem[]): Record<string, unknown> {
    return {
      '@context': 'https://schema.org',
      '@type': 'BreadcrumbList',
      itemListElement: items.map((item, index) => ({
        '@type': 'ListItem',
        position: index + 1,
        name: item.name,
        item: resolveCanonical(item.path),
      })),
    }
  }

  function buildCollectionPageSchema(options: {
    name: string
    description?: string | null
    path: string
    image?: string | null
  }): Record<string, unknown> {
    const image = resolveImage(options.image)

    return {
      '@context': 'https://schema.org',
      '@type': 'CollectionPage',
      name: options.name,
      description: getSiteDescription(options.description),
      url: resolveCanonical(options.path),
      inLanguage: locale.value,
      primaryImageOfPage: image,
      image,
    }
  }

  function buildWebPageSchema(options: {
    type?: 'WebPage' | 'AboutPage'
    name: string
    description?: string | null
    path: string
    image?: string | null
  }): Record<string, unknown> {
    const image = resolveImage(options.image)

    return {
      '@context': 'https://schema.org',
      '@type': options.type || 'WebPage',
      name: options.name,
      description: getSiteDescription(options.description),
      url: resolveCanonical(options.path),
      inLanguage: locale.value,
      primaryImageOfPage: image,
      image,
    }
  }

  function buildBlogPostingSchema(options: {
    title: string
    description?: string | null
    path: string
    image?: string | null
    author?: string | null
    publishedTime?: string | null
    modifiedTime?: string | null
    category?: string | null
    tags?: string[]
  }): Record<string, unknown> {
    const image = resolveImage(options.image)

    return {
      '@context': 'https://schema.org',
      '@type': 'BlogPosting',
      headline: options.title,
      description: getSiteDescription(options.description),
      image: [image],
      url: resolveCanonical(options.path),
      mainEntityOfPage: resolveCanonical(options.path),
      inLanguage: locale.value,
      datePublished: options.publishedTime || undefined,
      dateModified: options.modifiedTime || options.publishedTime || undefined,
      articleSection: options.category || undefined,
      keywords: options.tags?.length ? options.tags.join(', ') : undefined,
      author: options.author
        ? {
            '@type': 'Person',
            name: options.author,
          }
        : undefined,
      publisher: {
        '@type': 'Organization',
        name: SITE_NAME,
        founder: {
          '@type': 'Person',
          name: 'FakeJack',
        },
        logo: {
          '@type': 'ImageObject',
          url: toAbsoluteUrl(siteUrl, SITE_LOGO),
        },
      },
    }
  }

  return {
    siteName: SITE_NAME,
    siteDescription: SITE_DESCRIPTION,
    defaultSocialImage: resolveImage(DEFAULT_SOCIAL_IMAGE),
    resolveCanonical,
    resolveImage,
    summarizeHtml: (html: string, maxLength = 160) => {
      const text = stripHtml(html)
      if (text.length <= maxLength) {
        return text
      }

      return `${text.slice(0, maxLength - 1).trimEnd()}...`
    },
    applySeo,
    addStructuredData,
    buildWebsiteSchema,
    buildBreadcrumbSchema,
    buildCollectionPageSchema,
    buildWebPageSchema,
    buildBlogPostingSchema,
  }
}
