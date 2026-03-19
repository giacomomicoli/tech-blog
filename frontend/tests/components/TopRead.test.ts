import { describe, it, expect } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import TopRead from '~/components/TopRead.vue'
import type { Post } from '~/types/blog'

function makePost(overrides: Partial<Post> = {}): Post {
  return {
    id: 'p1',
    slug: 'test-post',
    title: 'Test Post',
    excerpt: 'Excerpt',
    category: 'Tech',
    tags: [],
    published_date: '2026-02-01',
    cover_image: 'https://example.com/cover.jpg',
    author: 'Alice',
    language: 'it',
    top: true,
    ...overrides,
  }
}

const topPosts: Post[] = [
  makePost({ id: 't1', slug: 'top-1', title: 'Top Post 1' }),
  makePost({ id: 't2', slug: 'top-2', title: 'Top Post 2' }),
]

describe('TopRead', () => {
  it('renders heading', async () => {
    const wrapper = await mountSuspended(TopRead, { props: { posts: topPosts } })
    expect(wrapper.find('.top-read__heading').exists()).toBe(true)
  })

  it('renders post titles', async () => {
    const wrapper = await mountSuspended(TopRead, { props: { posts: topPosts } })
    expect(wrapper.text()).toContain('Top Post 1')
    expect(wrapper.text()).toContain('Top Post 2')
  })

  it('renders thumbnails', async () => {
    const wrapper = await mountSuspended(TopRead, { props: { posts: topPosts } })
    const imgs = wrapper.findAll('img')
    expect(imgs.length).toBe(2)
    expect(imgs[0].attributes('src')).toBe('https://example.com/cover.jpg')
  })

  it('links to post slugs', async () => {
    const wrapper = await mountSuspended(TopRead, { props: { posts: topPosts } })
    const links = wrapper.findAll('a')
    expect(links.some(l => l.attributes('href')?.includes('/blog/top-1'))).toBe(true)
  })

  it('renders nothing when posts is empty', async () => {
    const wrapper = await mountSuspended(TopRead, { props: { posts: [] } })
    expect(wrapper.find('.top-read').exists()).toBe(false)
  })
})
