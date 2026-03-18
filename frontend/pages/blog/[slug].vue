<script setup lang="ts">
const route = useRoute()
const { locale } = useI18n()
const { t } = useI18n()
const localePath = useLocalePath()
const slug = route.params.slug as string
const { getPost } = useApi()

const { data: post, error } = await useAsyncData(`post-${locale.value}-${slug}`, () => getPost(locale.value, slug), {
  watch: [locale],
})

if (error.value) {
  throw createError({ statusCode: 404, statusMessage: t('post.notFound') })
}

useHead({ title: post.value?.title })

useSeoMeta({
  description: post.value?.excerpt,
  ogTitle: post.value?.title ? `${post.value.title} | No Hype, Just Vibe` : 'No Hype, Just Vibe',
  ogDescription: post.value?.excerpt,
  ogImage: post.value?.cover_image || undefined,
  ogType: 'article',
  twitterCard: 'summary_large_image',
  ogLocale: locale.value,
})
</script>

<template>
  <article v-if="post" class="post-page">
    <NuxtLink :to="localePath('/')" class="backhome">{{ t('post.backToBlog') }}</NuxtLink>

    <header class="post-header">
      <h1 class="post-title">{{ post.title }}</h1>
      <PostMeta :post="post" />
    </header>

    <figure v-if="post.cover_image" class="post-hero">
      <img :src="post.cover_image" :alt="post.title" />
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
