import type { Post, PostList } from '~/types/blog'

export function useApi() {
  const config = useRuntimeConfig()

  const baseUrl = import.meta.server
    ? config.backendUrl
    : config.public.backendUrl

  async function fetchApi<T>(path: string, params?: Record<string, string>): Promise<T> {
    const query = params
      ? '?' + new URLSearchParams(params).toString()
      : ''
    return await $fetch<T>(`${baseUrl}${path}${query}`)
  }

  async function getPosts(lang: string, opts?: {
    tag?: string
    category?: string
    featured?: boolean
    page?: number
    limit?: number
  }): Promise<PostList> {
    const params: Record<string, string> = { lang }
    if (opts?.tag) params.tag = opts.tag
    if (opts?.category) params.category = opts.category
    if (opts?.featured !== undefined) params.featured = String(opts.featured)
    if (opts?.page) params.page = String(opts.page)
    if (opts?.limit) params.limit = String(opts.limit)
    return fetchApi<PostList>('/api/posts', params)
  }

  async function getFeaturedPosts(lang: string, limit?: number): Promise<PostList> {
    return getPosts(lang, { featured: true, limit: limit ?? 5 })
  }

  async function getPost(lang: string, slug: string): Promise<Post> {
    return fetchApi<Post>(`/api/posts/${slug}`, { lang })
  }

  async function getCategories(lang: string): Promise<string[]> {
    return fetchApi<string[]>('/api/categories', { lang })
  }

  async function getTags(lang: string): Promise<string[]> {
    return fetchApi<string[]>('/api/tags', { lang })
  }

  async function getHeroPosts(lang: string): Promise<Post[]> {
    return fetchApi<Post[]>('/api/posts/hero', { lang })
  }

  async function getTopPosts(lang: string): Promise<Post[]> {
    return fetchApi<Post[]>('/api/posts/top', { lang })
  }

  async function getPage(lang: string, slug: string): Promise<{ slug: string; title: string; content_html: string }> {
    return fetchApi(`/api/pages/${slug}`, { lang })
  }

  return { getPosts, getFeaturedPosts, getPost, getCategories, getTags, getHeroPosts, getTopPosts, getPage }
}
