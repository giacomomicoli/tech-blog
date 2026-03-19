export interface Post {
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
