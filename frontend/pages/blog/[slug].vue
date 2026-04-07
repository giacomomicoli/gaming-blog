<script setup lang="ts">
const route = useRoute()
const { locale, t } = useI18n()
const localePath = useLocalePath()
const slug = computed(() => route.params.slug as string)
const { getPost } = useApi()
const {
  applySeo,
  addStructuredData,
  buildBlogPostingSchema,
  buildBreadcrumbSchema,
  defaultSocialImage,
} = useSeo()

const { data: post, error } = await useAsyncData(`post-${locale.value}-${slug.value}`, () => getPost(locale.value, slug.value), {
  watch: [locale, slug],
})

if (error.value) {
  throw createError({ statusCode: 404, statusMessage: t('post.notFound') })
}

const postPath = computed(() => `/${locale.value}/blog/${slug.value}`)
const postImage = computed(() => post.value?.social_image || post.value?.cover_image || defaultSocialImage)
const postDescription = computed(() => post.value?.meta_description || post.value?.excerpt)
const postAlternates = computed(() => {
  const alternates = post.value?.alternates || {}

  return Object.fromEntries(
    Object.entries(alternates).map(([lang, alternateSlug]) => [lang, `/${lang}/blog/${alternateSlug}`]),
  )
})

applySeo(() => ({
  title: post.value?.title || 'No Hype, Just Vibe',
  description: postDescription.value,
  path: postPath.value,
  image: postImage.value,
  imageAlt: post.value?.title,
  type: 'article',
  alternates: Object.keys(postAlternates.value).length ? postAlternates.value : undefined,
  publishedTime: post.value?.published_date,
  modifiedTime: post.value?.last_edited_time || post.value?.published_date,
  tags: post.value?.tags,
}))

addStructuredData(() => ([
  buildBlogPostingSchema({
    title: post.value?.title || 'No Hype, Just Vibe',
    description: postDescription.value,
    path: postPath.value,
    image: postImage.value,
    author: post.value?.author,
    publishedTime: post.value?.published_date,
    modifiedTime: post.value?.last_edited_time || post.value?.published_date,
    category: post.value?.category,
    tags: post.value?.tags,
  }),
  buildBreadcrumbSchema([
    { name: 'No Hype, Just Vibe', path: `/${locale.value}` },
    { name: post.value?.category || t('category.breadcrumb'), path: `/${locale.value}` },
    { name: post.value?.title || 'Post', path: postPath.value },
  ]),
]), 'blog-post')
</script>

<template>
  <article v-if="post" class="post-page">
    <NuxtLink :to="localePath('/')" class="backhome">{{ t('post.backToBlog') }}</NuxtLink>

    <header class="post-header">
      <h1 class="post-title">{{ post.title }}</h1>
      <PostMeta :post="post" />
    </header>

    <figure v-if="post.cover_image" class="post-hero">
      <img :src="post.cover_image" :alt="post.title" loading="eager" fetchpriority="high" decoding="async" />
    </figure>

    <div class="post-layout">
      <div class="notion-content" v-html="post.content_html" />
      <aside v-if="post.table_of_contents && post.table_of_contents.length > 0" class="post-sidebar">
        <TableOfContents :entries="post.table_of_contents" />
      </aside>
    </div>
  </article>
</template>

<style scoped>
.post-page {
  max-width: var(--container-xl);
}

.backhome {
  display: inline-flex;
  align-items: center;
  min-height: var(--touch-target-min);
  font-size: var(--font-size-base);
  margin-block: var(--space-sm);
  padding: var(--space-xs) 0;
}

.post-header {
  margin-block-end: var(--space-md);
}

.post-title {
  font-size: var(--font-size-2xl);
  margin-block-end: var(--space-sm);
  word-wrap: break-word;
  overflow-wrap: break-word;
  hyphens: auto;
}

.post-hero {
  margin: var(--space-md) 0;
  padding: 0;
}

.post-hero img {
  display: block;
  width: 100%;
  height: auto;
  border-radius: var(--space-xs);
  object-fit: cover;
  max-height: 300px;
}

.post-layout {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-lg);
}

.post-sidebar {
  display: none;
}

@media screen and (min-width: 768px) {
  .post-title {
    font-size: var(--font-size-3xl);
  }

  .post-hero img {
    max-height: 400px;
  }
}

@media screen and (min-width: 1024px) {
  .post-title {
    font-size: var(--font-size-4xl);
  }

  .post-hero img {
    max-height: 500px;
  }

  .post-layout {
    grid-template-columns: 1fr 240px;
  }

  .post-sidebar {
    display: block;
  }
}
</style>
