import { describe, it, expect } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import HeroSection from '~/components/HeroSection.vue'
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
    hero_position: 1,
    ...overrides,
  }
}

const heroPosts: Post[] = [
  makePost({ id: 'h1', slug: 'hero-1', title: 'Hero Large', hero_position: 1 }),
  makePost({ id: 'h2', slug: 'hero-2', title: 'Hero Small 1', hero_position: 2 }),
  makePost({ id: 'h3', slug: 'hero-3', title: 'Hero Small 2', hero_position: 3 }),
]

describe('HeroSection', () => {
  it('renders large tile title', async () => {
    const wrapper = await mountSuspended(HeroSection, { props: { posts: heroPosts } })
    expect(wrapper.text()).toContain('Hero Large')
  })

  it('renders small tiles', async () => {
    const wrapper = await mountSuspended(HeroSection, { props: { posts: heroPosts } })
    expect(wrapper.text()).toContain('Hero Small 1')
    expect(wrapper.text()).toContain('Hero Small 2')
  })

  it('renders category badges', async () => {
    const wrapper = await mountSuspended(HeroSection, { props: { posts: heroPosts } })
    expect(wrapper.text()).toContain('Tech')
  })

  it('links to post slugs', async () => {
    const wrapper = await mountSuspended(HeroSection, { props: { posts: heroPosts } })
    const links = wrapper.findAll('a')
    const hrefs = links.map(l => l.attributes('href'))
    expect(hrefs.some(h => h?.includes('/blog/hero-1'))).toBe(true)
    expect(hrefs.some(h => h?.includes('/blog/hero-2'))).toBe(true)
  })

  it('renders nothing when posts is empty', async () => {
    const wrapper = await mountSuspended(HeroSection, { props: { posts: [] } })
    expect(wrapper.find('.hero-section').exists()).toBe(false)
  })
})
