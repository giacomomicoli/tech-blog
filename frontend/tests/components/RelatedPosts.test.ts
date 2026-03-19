import { describe, it, expect } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import RelatedPosts from '~/components/RelatedPosts.vue'
import type { Post } from '~/types/blog'

function makePost(overrides: Partial<Post> = {}): Post {
  return {
    id: 'p1',
    slug: 'test-post',
    title: 'Test Post',
    excerpt: 'Excerpt',
    category: 'Tech',
    tags: ['python'],
    published_date: '2026-02-01',
    cover_image: 'https://example.com/cover.jpg',
    author: 'Alice',
    language: 'it',
    ...overrides,
  }
}

const relatedPosts: Post[] = [
  makePost({ id: 'r1', slug: 'related-1', title: 'Related Post 1' }),
  makePost({ id: 'r2', slug: 'related-2', title: 'Related Post 2' }),
]

describe('RelatedPosts', () => {
  it('renders section heading', async () => {
    const wrapper = await mountSuspended(RelatedPosts, { props: { posts: relatedPosts } })
    expect(wrapper.find('.related-posts__heading').exists()).toBe(true)
  })

  it('renders post cards', async () => {
    const wrapper = await mountSuspended(RelatedPosts, { props: { posts: relatedPosts } })
    expect(wrapper.text()).toContain('Related Post 1')
    expect(wrapper.text()).toContain('Related Post 2')
  })

  it('renders nothing when posts is empty', async () => {
    const wrapper = await mountSuspended(RelatedPosts, { props: { posts: [] } })
    expect(wrapper.find('.related-posts').exists()).toBe(false)
  })
})
