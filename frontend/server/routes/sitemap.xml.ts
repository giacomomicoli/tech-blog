import { defineEventHandler } from 'h3'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const backendUrl = config.backendUrl
  const siteUrl = config.public.siteUrl
  const supportedLocales = (config.public.supportedLocales || 'it,en').split(',').map((s: string) => s.trim())

  const today = new Date().toISOString().split('T')[0]
  const urls: string[] = []

  // Static pages per locale with hreflang alternates
  const staticPages = ['', '/about-blog', '/about-me']
  for (const page of staticPages) {
    for (const lang of supportedLocales) {
      const loc = `${siteUrl}/${lang}${page}`
      const priority = page === '' ? '1.0' : '0.6'
      const alternates = supportedLocales
        .map(l => `    <xhtml:link rel="alternate" hreflang="${l}" href="${siteUrl}/${l}${page}" />`)
        .join('\n')
      urls.push(`  <url>
    <loc>${loc}</loc>
    <lastmod>${today}</lastmod>
    <priority>${priority}</priority>
${alternates}
  </url>`)
    }
  }

  // Posts per locale
  for (const lang of supportedLocales) {
    const allPosts: any[] = []
    let page = 1
    let hasMore = true
    while (hasMore) {
      const res = await $fetch<any>(`${backendUrl}/api/posts?limit=50&page=${page}&lang=${lang}`)
      allPosts.push(...(res.posts || []))
      hasMore = res.has_more
      page++
    }

    for (const post of allPosts) {
      const lastmod = post.published_date
        ? post.published_date.split('T')[0]
        : today
      urls.push(`  <url>
    <loc>${siteUrl}/${lang}/blog/${post.slug}</loc>
    <lastmod>${lastmod}</lastmod>
    <priority>0.8</priority>
  </url>`)
    }
  }

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">
${urls.join('\n')}
</urlset>`

  event.node.res.setHeader('content-type', 'application/xml; charset=utf-8')
  return xml
})
