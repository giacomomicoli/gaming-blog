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
  reading_time?: number
  content_html?: string
  table_of_contents?: TocEntry[]
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
