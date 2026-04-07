import { describe, expect, it } from 'vitest'
import { mountSuspended } from '@nuxt/test-utils/runtime'
import { defineComponent } from 'vue'

const TestSeoComponent = defineComponent({
  setup() {
    const { applySeo } = useSeo()
    const head = injectHead()
    ;(globalThis as { __testHead?: ReturnType<typeof injectHead> }).__testHead = head

    applySeo(() => ({
      title: 'SEO Test Post',
      description: 'SEO test description',
      path: '/it/blog/seo-test-post',
      image: 'https://example.com/social-card.jpg',
      imageAlt: 'SEO Test Post',
      type: 'article',
      publishedTime: '2026-04-01',
      modifiedTime: '2026-04-02T12:00:00.000Z',
      tags: ['test', 'seo'],
    }))

    return () => null
  },
})

function findTag(
  tags: Array<{ tag: string, props?: Record<string, string>, textContent?: string }>,
  tagName: string,
  predicate: (tag: { tag: string, props?: Record<string, string>, textContent?: string }) => boolean
) {
  return tags.find(tag => tag.tag === tagName && predicate(tag))
}

describe('useSeo', () => {
  it('resolves article SEO tags through Unhead', async () => {
    await mountSuspended(TestSeoComponent)

    const head = (globalThis as { __testHead?: ReturnType<typeof injectHead> }).__testHead
    const tags = await head?.resolveTags()

    expect(tags).toBeDefined()

    expect(findTag(tags || [], 'title', tag => tag.textContent === 'SEO Test Post')).toBeDefined()
    expect(findTag(tags || [], 'link', tag => tag.props?.rel === 'canonical' && tag.props?.href === 'https://gaming.fakejack.dev/it/blog/seo-test-post')).toBeDefined()
    expect(findTag(tags || [], 'meta', tag => tag.props?.name === 'description' && tag.props?.content === 'SEO test description')).toBeDefined()
    expect(findTag(tags || [], 'meta', tag => tag.props?.name === 'robots' && tag.props?.content === 'index,follow,max-image-preview:large')).toBeDefined()
    expect(findTag(tags || [], 'meta', tag => tag.props?.property === 'og:title' && tag.props?.content === 'SEO Test Post | No Hype, Just Vibe')).toBeDefined()
    expect(findTag(tags || [], 'meta', tag => tag.props?.property === 'og:description' && tag.props?.content === 'SEO test description')).toBeDefined()
    expect(findTag(tags || [], 'meta', tag => tag.props?.property === 'og:url' && tag.props?.content === 'https://gaming.fakejack.dev/it/blog/seo-test-post')).toBeDefined()
    expect(findTag(tags || [], 'meta', tag => tag.props?.property === 'og:type' && tag.props?.content === 'article')).toBeDefined()
    expect(findTag(tags || [], 'meta', tag => tag.props?.property === 'og:image' && tag.props?.content === 'https://example.com/social-card.jpg')).toBeDefined()
    expect(findTag(tags || [], 'meta', tag => tag.props?.name === 'twitter:card' && tag.props?.content === 'summary_large_image')).toBeDefined()
    expect(findTag(tags || [], 'meta', tag => tag.props?.name === 'twitter:title' && tag.props?.content === 'SEO Test Post | No Hype, Just Vibe')).toBeDefined()
    expect(findTag(tags || [], 'meta', tag => tag.props?.name === 'twitter:description' && tag.props?.content === 'SEO test description')).toBeDefined()
    expect(findTag(tags || [], 'meta', tag => tag.props?.name === 'twitter:image' && tag.props?.content === 'https://example.com/social-card.jpg')).toBeDefined()
    expect(findTag(tags || [], 'meta', tag => tag.props?.property === 'article:published_time' && tag.props?.content === '2026-04-01')).toBeDefined()
    expect(findTag(tags || [], 'meta', tag => tag.props?.property === 'article:modified_time' && tag.props?.content === '2026-04-02T12:00:00.000Z')).toBeDefined()
  })
})
