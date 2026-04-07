import { defineEventHandler } from 'h3'

export default defineEventHandler((event) => {
  const config = useRuntimeConfig()
  const siteUrl = (config.public.siteUrl || 'http://localhost:3000').replace(/\/+$/, '')

  const text = [
    'User-agent: *',
    'Allow: /',
    '',
    `Sitemap: ${siteUrl}/sitemap.xml`,
  ].join('\n')

  event.node.res.setHeader('content-type', 'text/plain; charset=utf-8')
  return text
})
