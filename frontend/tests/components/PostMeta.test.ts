import { describe, it, expect } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import PostMeta from '~/components/PostMeta.vue'
import type { Post } from '~/types/blog'

const basePost: Post = {
  id: 'p1',
  slug: 'test-post',
  title: 'Test Post',
  excerpt: '',
  category: 'Tech',
  tags: ['python', 'api'],
  published_date: '2026-02-01',
  cover_image: null,
  author: 'Alice',
  reading_time: 5,
  language: 'it',
}

describe('PostMeta', () => {
  it('renders author', async () => {
    const wrapper = await mountSuspended(PostMeta, { props: { post: basePost } })
    expect(wrapper.text()).toContain('Alice')
  })

  it('renders reading time', async () => {
    const wrapper = await mountSuspended(PostMeta, { props: { post: basePost } })
    expect(wrapper.text()).toContain('5')
  })

  it('renders category as link', async () => {
    const wrapper = await mountSuspended(PostMeta, { props: { post: basePost } })
    const link = wrapper.find('.post-meta-category')
    expect(link.text()).toBe('Tech')
    expect(link.attributes('href')).toContain('/category/Tech')
  })

  it('renders tag links', async () => {
    const wrapper = await mountSuspended(PostMeta, { props: { post: basePost } })
    const tags = wrapper.findAll('.tag')
    expect(tags).toHaveLength(2)
    expect(tags[0].text()).toBe('python')
    expect(tags[0].attributes('href')).toContain('/tag/python')
  })

  it('hides category when null', async () => {
    const post = { ...basePost, category: null }
    const wrapper = await mountSuspended(PostMeta, { props: { post } })
    expect(wrapper.find('.post-meta-category').exists()).toBe(false)
  })

  it('hides tags section when empty', async () => {
    const post = { ...basePost, tags: [] }
    const wrapper = await mountSuspended(PostMeta, { props: { post } })
    expect(wrapper.find('.post-meta-tags').exists()).toBe(false)
  })

  it('hides author when empty', async () => {
    const post = { ...basePost, author: '' }
    const wrapper = await mountSuspended(PostMeta, { props: { post } })
    expect(wrapper.find('.post-meta-author').exists()).toBe(false)
  })
})
