import { defineEventHandler, getQuery } from 'h3'

export default defineEventHandler(async (event) => {
  const config = useRuntimeConfig()
  const backendUrl = config.backendUrl
  const siteUrl = config.public.siteUrl
  const defaultLocale = config.public.defaultLocale || 'it'
  const supportedLocales = (config.public.supportedLocales || 'it,en').split(',').map((s: string) => s.trim())

  const query = getQuery(event)
  const lang = supportedLocales.includes(query.lang as string) ? (query.lang as string) : defaultLocale

  const posts = await $fetch<any>(`${backendUrl}/api/posts?limit=50&lang=${lang}`)
  const items = (posts.posts || [])
    .map((post: any) => {
      const pubDate = post.published_date
        ? new Date(post.published_date).toUTCString()
        : new Date().toUTCString()
      return `    <item>
      <title><![CDATA[${post.title}]]></title>
      <link>${siteUrl}/${lang}/blog/${post.slug}</link>
      <guid>${siteUrl}/${lang}/blog/${post.slug}</guid>
      <pubDate>${pubDate}</pubDate>
      <description><![CDATA[${post.excerpt || ''}]]></description>
      ${post.category ? `<category>${post.category}</category>` : ''}
    </item>`
    })
    .join('\n')

  const xml = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>TECH.md</title>
    <link>${siteUrl}/${lang}</link>
    <description>TECH.md — A blog powered by Notion</description>
    <language>${lang}</language>
    <atom:link href="${siteUrl}/rss.xml?lang=${lang}" rel="self" type="application/rss+xml"/>
${items}
  </channel>
</rss>`

  event.node.res.setHeader('content-type', 'application/rss+xml; charset=utf-8')
  return xml
})
