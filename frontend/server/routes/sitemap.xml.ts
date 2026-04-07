import { defineEventHandler } from 'h3'

interface PostListItem {
  slug: string
  published_date?: string | null
  last_edited_time?: string | null
  translation_key?: string | null
}

interface PostListResponse {
  posts: PostListItem[]
  has_more: boolean
}

interface StaticPageResponse {
  slug: string
  last_edited_time?: string | null
  alternates?: Record<string, string>
}

function formatDate(value?: string | null): string | null {
  if (!value) {
    return null
  }

  return value.split('T')[0]
}

function escapeXml(value: string): string {
  return value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')
}

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const backendUrl = config.backendUrl
  const siteUrl = (config.public.siteUrl || 'http://localhost:3000').replace(/\/+$/, '')
  const defaultLocale = config.public.defaultLocale || 'it'
  const supportedLocales = (config.public.supportedLocales || 'it,en')
    .split(',')
    .map((s: string) => s.trim())
    .filter(Boolean)

  const today = new Date().toISOString().split('T')[0]
  const urls: string[] = []
  const postsByLocale: Record<string, PostListItem[]> = {}
  const alternatesByTranslationKey: Record<string, Record<string, string>> = {}
  const homepageAlternates = supportedLocales.reduce<Record<string, string>>((map, locale) => {
    map[locale] = `/${locale}`
    return map
  }, {})

  for (const locale of supportedLocales) {
    const staticPages = [
      {
        slug: '',
        path: `/${locale}`,
        priority: '1.0',
        alternates: homepageAlternates,
      },
      {
        slug: 'about-blog',
        path: `/${locale}/about-blog`,
        priority: '0.7',
      },
      {
        slug: 'about-me',
        path: `/${locale}/about-me`,
        priority: '0.6',
      },
    ]

    for (const staticPage of staticPages) {
      let lastmod = today
      let alternates = staticPage.alternates || {}

      if (staticPage.slug) {
        try {
          const page = await $fetch<StaticPageResponse>(`${backendUrl}/api/pages/${staticPage.slug}?lang=${locale}`)
          lastmod = formatDate(page.last_edited_time) || today

          if (page.alternates && Object.keys(page.alternates).length) {
            alternates = Object.fromEntries(
              Object.keys(page.alternates).map(lang => [lang, `/${lang}/${staticPage.slug}`]),
            )
          }
        }
        catch {
          continue
        }
      }

      const alternateLinks = Object.entries(alternates)
        .map(([lang, path]) => `    <xhtml:link rel="alternate" hreflang="${escapeXml(lang)}" href="${escapeXml(`${siteUrl}${path}`)}" />`)
        .join('\n')

      const xDefaultPath = alternates[defaultLocale]
      const xDefaultLink = xDefaultPath
        ? `\n    <xhtml:link rel="alternate" hreflang="x-default" href="${escapeXml(`${siteUrl}${xDefaultPath}`)}" />`
        : ''

      urls.push(`  <url>
    <loc>${escapeXml(`${siteUrl}${staticPage.path}`)}</loc>
    <lastmod>${lastmod}</lastmod>
    <priority>${staticPage.priority}</priority>
${alternateLinks}${xDefaultLink}
  </url>`)
    }

    const allPosts: PostListItem[] = []
    let page = 1
    let hasMore = true

    while (hasMore) {
      const response = await $fetch<PostListResponse>(`${backendUrl}/api/posts?limit=50&page=${page}&lang=${locale}`)
      allPosts.push(...(response.posts || []))
      hasMore = response.has_more
      page += 1
    }

    postsByLocale[locale] = allPosts

    allPosts.forEach((post) => {
      if (!post.translation_key) {
        return
      }

      const existingAlternates = alternatesByTranslationKey[post.translation_key] || {}
      existingAlternates[locale] = `/${locale}/blog/${post.slug}`
      alternatesByTranslationKey[post.translation_key] = existingAlternates
    })
  }

  for (const locale of supportedLocales) {
    const allPosts = postsByLocale[locale] || []
    for (const post of allPosts) {
      const alternates = post.translation_key ? alternatesByTranslationKey[post.translation_key] || {} : {}
      const mappedLinks = Object.entries(alternates)
        .map(([lang, path]) => `    <xhtml:link rel="alternate" hreflang="${escapeXml(lang)}" href="${escapeXml(`${siteUrl}${path}`)}" />`)
        .join('\n')
      const xDefaultPath = alternates[defaultLocale]
      const xDefaultLink = xDefaultPath
        ? `\n    <xhtml:link rel="alternate" hreflang="x-default" href="${escapeXml(`${siteUrl}${xDefaultPath}`)}" />`
        : ''
      const alternateLinks = Object.keys(alternates).length > 1
        ? `${mappedLinks}${xDefaultLink}`
        : ''

      const lastmod = formatDate(post.last_edited_time || post.published_date) || today
      urls.push(`  <url>
    <loc>${escapeXml(`${siteUrl}/${locale}/blog/${post.slug}`)}</loc>
    <lastmod>${lastmod}</lastmod>
    <priority>0.8</priority>
${alternateLinks ? `${alternateLinks}\n` : ''}  </url>`)
    }
  }

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
${urls.join('\n')}
</urlset>`

  event.node.res.setHeader('content-type', 'application/xml; charset=utf-8')
  return xml
})
