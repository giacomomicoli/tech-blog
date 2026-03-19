import { describe, it, expect } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import TableOfContents from '~/components/TableOfContents.vue'
import type { TocEntry } from '~/types/blog'

const entries: TocEntry[] = [
  { id: 'intro', text: 'Introduction', level: 1 },
  { id: 'setup', text: 'Setup', level: 2 },
  { id: 'details', text: 'Details', level: 3 },
]

describe('TableOfContents', () => {
  it('renders all entries', async () => {
    const wrapper = await mountSuspended(TableOfContents, { props: { entries } })
    expect(wrapper.text()).toContain('Introduction')
    expect(wrapper.text()).toContain('Setup')
    expect(wrapper.text()).toContain('Details')
  })

  it('renders title', async () => {
    const wrapper = await mountSuspended(TableOfContents, { props: { entries } })
    const title = wrapper.find('.toc-title')
    expect(title.exists()).toBe(true)
    expect(title.text().length).toBeGreaterThan(0)
  })

  it('links to heading ids', async () => {
    const wrapper = await mountSuspended(TableOfContents, { props: { entries } })
    const links = wrapper.findAll('a')
    expect(links[0].attributes('href')).toBe('#intro')
    expect(links[1].attributes('href')).toBe('#setup')
    expect(links[2].attributes('href')).toBe('#details')
  })

  it('applies level classes for indentation', async () => {
    const wrapper = await mountSuspended(TableOfContents, { props: { entries } })
    const items = wrapper.findAll('li')
    expect(items[0].classes()).toContain('toc-level-1')
    expect(items[1].classes()).toContain('toc-level-2')
    expect(items[2].classes()).toContain('toc-level-3')
  })

  it('hides when entries are empty', async () => {
    const wrapper = await mountSuspended(TableOfContents, { props: { entries: [] } })
    expect(wrapper.find('nav').exists()).toBe(false)
  })
})
