export interface AlternatesMap {
  [locale: string]: string
}

export interface SeoMetadata {
  social_image?: string | null
  meta_description?: string | null
  translation_key?: string | null
  last_edited_time?: string | null
  alternates?: AlternatesMap
}

export interface Post extends SeoMetadata {
  id: string
  slug: string
  title: string
  excerpt: string
  category: string | null
  tags: string[]
  published_date: string | null
  cover_image: string | null
  author: string
  featured?: boolean
  language: string
  hero_position?: number | null
  top?: boolean
  reading_time?: number
  content_html?: string
  table_of_contents?: TocEntry[]
  related_posts?: Post[]
}

export interface StaticPage extends SeoMetadata {
  id: string
  slug: string
  title: string
  language: string
  content_html: string
}

export interface TocEntry {
  id: string
  text: string
  level: number
}

export interface PostList {
  posts: Post[]
  total: number
  page: number
  has_more: boolean
}
