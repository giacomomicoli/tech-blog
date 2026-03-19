import { existsSync } from 'node:fs'
import { resolve } from 'node:path'

const theme = process.env.NUXT_THEME || 'tech-dark'
const themePath = resolve(__dirname, `assets/themes/${theme}/theme.css`)

if (!existsSync(themePath)) {
  console.error(`[nuxt] Theme "${theme}" not found at ${themePath}, falling back to tech-dark`)
}

const resolvedTheme = existsSync(themePath) ? theme : 'tech-dark'

export default defineNuxtConfig({
  compatibilityDate: '2025-01-01',
  devtools: { enabled: true },
  ssr: true,

  modules: ['@nuxtjs/i18n'],

  i18n: {
    locales: (process.env.SUPPORTED_LOCALES || 'it,en').split(',').map(code => ({
      code: code.trim(),
      file: `${code.trim()}.json`,
    })),
    defaultLocale: process.env.DEFAULT_LOCALE || 'it',
    langDir: '../locales',
    strategy: 'prefix',
    detectBrowserLanguage: false,
    rootRedirect: { path: '', statusCode: 302 },
  },

  css: [
    `~/assets/themes/${resolvedTheme}/theme.css`,
    '~/assets/css/main.css',
    '~/assets/css/notion-content.css',
  ],

  runtimeConfig: {
    backendUrl: process.env.BACKEND_URL || 'http://backend:8000',
    public: {
      backendUrl: process.env.NUXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost:3000',
      defaultLocale: process.env.DEFAULT_LOCALE || 'it',
      supportedLocales: process.env.SUPPORTED_LOCALES || 'it,en',
    },
  },

  app: {
    pageTransition: { name: 'page', mode: 'out-in' },
    head: {
      charset: 'utf-8',
      viewport: 'width=device-width, initial-scale=1',
      title: 'TECH.md',
      titleTemplate: '%s | TECH.md',
      meta: [
        { name: 'description', content: 'TECH.md — A blog powered by Notion' },
      ],
      link: [
        { rel: 'icon', href: '/favicon.ico', sizes: 'any' },
        { rel: 'icon', type: 'image/svg+xml', href: '/favicon.svg' },
        { rel: 'icon', type: 'image/png', sizes: '96x96', href: '/favicon-96x96.png' },
        { rel: 'apple-touch-icon', sizes: '180x180', href: '/apple-touch-icon.png' },
        { rel: 'manifest', href: '/site.webmanifest' },
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Mono:ital,wght@0,200..800;1,200..800&display=swap' },
        { rel: 'alternate', type: 'application/rss+xml', title: 'TECH.md RSS', href: '/rss.xml' },
      ],
    },
  },
})
