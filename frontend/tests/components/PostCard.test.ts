import { describe, it, expect } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import PostCard from '~/components/PostCard.vue'
import type { Post } from '~/types/blog'

const basePost: Post = {
  id: 'p1',
  slug: 'test-post',
  title: 'Test Post Title',
  excerpt: 'This is a test excerpt.',
  category: 'Tech',
  tags: ['python', 'api'],
  published_date: '2026-02-01',
  cover_image: 'https://example.com/cover.jpg',
  author: 'Alice',
  reading_time: 5,
  language: 'it',
}

describe('PostCard', () => {
  it('renders title', async () => {
    const wrapper = await mountSuspended(PostCard, { props: { post: basePost } })
    expect(wrapper.text()).toContain('Test Post Title')
  })

  it('renders excerpt', async () => {
    const wrapper = await mountSuspended(PostCard, { props: { post: basePost } })
    expect(wrapper.text()).toContain('This is a test excerpt.')
  })

  it('renders category badge', async () => {
    const wrapper = await mountSuspended(PostCard, { props: { post: basePost } })
    expect(wrapper.text()).toContain('Tech')
  })

  it('renders tags', async () => {
    const wrapper = await mountSuspended(PostCard, { props: { post: basePost } })
    expect(wrapper.text()).toContain('python')
    expect(wrapper.text()).toContain('api')
  })

  it('renders reading time', async () => {
    const wrapper = await mountSuspended(PostCard, { props: { post: basePost } })
    expect(wrapper.text()).toContain('5')
  })

  it('renders cover image', async () => {
    const wrapper = await mountSuspended(PostCard, { props: { post: basePost } })
    const img = wrapper.find('img')
    expect(img.exists()).toBe(true)
    expect(img.attributes('src')).toBe('https://example.com/cover.jpg')
  })

  it('hides cover image when null', async () => {
    const post = { ...basePost, cover_image: null }
    const wrapper = await mountSuspended(PostCard, { props: { post } })
    expect(wrapper.find('img').exists()).toBe(false)
  })

  it('links to locale-prefixed post slug', async () => {
    const wrapper = await mountSuspended(PostCard, { props: { post: basePost } })
    const links = wrapper.findAll('a')
    const postLinks = links.filter(l => l.attributes('href')?.includes('/blog/'))
    expect(postLinks.length).toBeGreaterThan(0)
    expect(postLinks[0].attributes('href')).toContain('/blog/test-post')
  })

  it('hides reading time when not provided', async () => {
    const post = { ...basePost, reading_time: undefined }
    const wrapper = await mountSuspended(PostCard, { props: { post } })
    const timeEl = wrapper.find('time')
    expect(timeEl.text()).not.toContain('·')
  })

  it('formats date correctly', async () => {
    const wrapper = await mountSuspended(PostCard, { props: { post: basePost } })
    expect(wrapper.text()).toContain('2026')
  })
})
