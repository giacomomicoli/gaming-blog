<script setup lang="ts">
const { locale, t } = useI18n()
const { getPosts, getFeaturedPosts } = useApi()
const { applySeo, addStructuredData, buildBreadcrumbSchema, buildCollectionPageSchema, defaultSocialImage } = useSeo()
const page = ref(1)

const { data, status } = await useAsyncData(`posts-${locale.value}`, () => getPosts(locale.value, { page: page.value }), {
  watch: [page, locale],
})

const { data: featuredData } = await useAsyncData(`featured-posts-${locale.value}`, () => getFeaturedPosts(locale.value, 5), {
  watch: [locale],
})

const pageTitle = 'No Hype, Just Vibe'
const pageDescription = computed(() => {
  if (featuredData.value?.posts?.[0]?.excerpt) {
    return featuredData.value.posts[0].excerpt
  }

  return locale.value === 'it'
    ? 'Recensioni, cultura gaming e articoli selezionati con un tono editoriale pulito e leggibile.'
    : 'Reviews, gaming culture, and curated articles with a clean editorial voice.'
})

const homepageAlternates = computed(() => ({
  it: '/it',
  en: '/en',
}))

applySeo(() => ({
  title: pageTitle,
  description: pageDescription.value,
  path: `/${locale.value}`,
  image: featuredData.value?.posts?.[0]?.social_image || featuredData.value?.posts?.[0]?.cover_image || defaultSocialImage,
  imageAlt: pageTitle,
  noTemplate: true,
  alternates: homepageAlternates.value,
}))

addStructuredData(() => ([
  buildCollectionPageSchema({
    name: pageTitle,
    description: pageDescription.value,
    path: `/${locale.value}`,
    image: featuredData.value?.posts?.[0]?.social_image || featuredData.value?.posts?.[0]?.cover_image || defaultSocialImage,
  }),
  buildBreadcrumbSchema([
    { name: pageTitle, path: `/${locale.value}` },
  ]),
]), 'homepage')

function nextPage() {
  if (data.value?.has_more) page.value++
}

function prevPage() {
  if (page.value > 1) page.value--
}
</script>

<template>
  <div>
    <h1 class="page-title">{{ pageTitle }}</h1>
    <HeroCarousel v-if="featuredData?.posts.length" :posts="featuredData.posts" />

    <h2 class="section-title">{{ t('home.latestPosts') }}</h2>

    <div v-if="status === 'pending'" class="loading">{{ t('home.loading') }}</div>

    <div v-else-if="data && data.posts.length > 0">
      <div class="post-grid">
        <PostCard v-for="post in data.posts" :key="post.id" :post="post" />
      </div>

      <nav v-if="data.total > 10" class="pagination">
        <button :disabled="page <= 1" @click="prevPage">{{ t('pagination.previous') }}</button>
        <span class="pagination-info">{{ t('pagination.page', { page }) }}</span>
        <button :disabled="!data.has_more" @click="nextPage">{{ t('pagination.next') }}</button>
      </nav>
    </div>

    <div v-else class="empty">
      <p>{{ t('home.noPosts') }}</p>
    </div>
  </div>
</template>

<style scoped>
.page-title {
  margin: 0 0 var(--space-sm);
  font-size: var(--font-size-2xl);
}

.section-title {
  margin: 0 0 var(--space-lg);
}

@media screen and (min-width: 768px) {
  .page-title {
    font-size: var(--font-size-3xl);
  }
}

.post-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--space-md);
}

@media screen and (min-width: 1200px) {
  .post-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--space-sm);
  margin-top: var(--space-xl);
}

.pagination button {
  display: inline-flex;
  align-items: center;
  min-height: var(--touch-target-min);
  padding: var(--space-xs) var(--space-sm);
  font-family: var(--font-family);
  font-size: var(--font-size-base);
  font-weight: 600;
  border: none;
  border-radius: var(--space-xs);
  background-color: var(--a-color);
  color: var(--background-color);
  cursor: pointer;
  transition: background-color var(--transition-base);
}

.pagination button:hover:not(:disabled) {
  background-color: var(--a-color-hover);
}

.pagination button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.pagination-info {
  font-size: var(--font-size-sm);
  color: var(--font-color-muted);
}

.loading,
.empty {
  text-align: center;
  color: var(--font-color-muted);
  padding: var(--space-2xl) 0;
}
</style>
