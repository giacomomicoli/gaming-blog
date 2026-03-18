<script setup lang="ts">
import type { Post } from '~/types/blog'

defineProps<{ post: Post }>()

const { locale, t } = useI18n()
const localePath = useLocalePath()

function formatDate(date: string | null): string {
  if (!date) return ''
  return new Date(date).toLocaleDateString(locale.value, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}
</script>

<template>
  <article class="post-preview">
    <div v-if="post.cover_image" class="post-preview-cover">
      <NuxtLink :to="localePath(`/blog/${post.slug}`)">
        <img :src="post.cover_image" :alt="post.title" loading="lazy" />
      </NuxtLink>
    </div>
    <div class="post-preview-body">
      <header>
        <NuxtLink v-if="post.category" :to="localePath(`/category/${post.category}`)" class="post-preview-category">{{ post.category }}</NuxtLink>
        <h2><NuxtLink :to="localePath(`/blog/${post.slug}`)">{{ post.title }}</NuxtLink></h2>
        <time v-if="post.published_date" :datetime="post.published_date">
          {{ formatDate(post.published_date) }}
          <em v-if="post.author"> {{ t('post.by') }} {{ post.author }}</em>
          <span v-if="post.reading_time"> &middot; {{ post.reading_time }} {{ t('post.minRead') }}</span>
        </time>
      </header>
      <p v-if="post.excerpt" class="excerpt">{{ post.excerpt }}</p>
      <div v-if="post.tags.length" class="post-preview-tags">
        <NuxtLink v-for="tag in post.tags" :key="tag" :to="localePath(`/tag/${tag}`)" class="tag">{{ tag }}</NuxtLink>
      </div>
      <footer>
        <NuxtLink :to="localePath(`/blog/${post.slug}`)" :aria-label="`Read more about ${post.title}`">{{ t('post.readMore') }}</NuxtLink>
      </footer>
    </div>
  </article>
</template>

<style scoped>
.post-preview {
  padding: var(--space-md);
  background-color: var(--surface-color);
  border-radius: var(--space-xs);
  border: 1px solid var(--border-color);
}

.post-preview-cover {
  margin: calc(-1 * var(--space-md));
  margin-bottom: var(--space-sm);
  overflow: hidden;
  border-radius: var(--space-xs) var(--space-xs) 0 0;
}

.post-preview-cover img {
  width: 100%;
  height: auto;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  display: block;
}

.post-preview header {
  padding: 0;
  margin-block-end: var(--space-sm);
  border-bottom: none;
}

.post-preview h2 {
  font-size: var(--font-size-lg);
  margin-block-end: var(--space-xs);
}

.post-preview h2 a {
  text-decoration: none;
  color: var(--font-color);
}
.post-preview h2 a:hover,
.post-preview h2 a:focus {
  text-decoration: underline;
  color: var(--a-color-hover);
}

.post-preview time {
  font-size: var(--font-size-sm);
  color: var(--font-color-muted);
  display: block;
}

.excerpt {
  font-size: var(--font-size-base);
  line-height: var(--line-height-relaxed);
  margin-block: var(--space-sm);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.post-preview-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-xs);
  margin-block-end: var(--space-sm);
}

.tag {
  background: var(--background-color);
  color: var(--font-color-muted);
  font-size: var(--font-size-xs);
  padding: 2px var(--space-xs);
  border-radius: 4px;
  text-decoration: none;
  border: 1px solid var(--border-color);
}

.tag:hover {
  color: var(--a-color);
  border-color: var(--a-color);
}

.post-preview footer {
  padding-block-start: var(--space-sm);
  padding: 0;
  margin: 0;
  border: none;
}

.post-preview footer a {
  display: inline-flex;
  align-items: center;
  min-height: var(--touch-target-min);
  padding: var(--space-xs) var(--space-sm);
  font-size: var(--font-size-base);
  font-weight: 600;
  text-decoration: none;
  white-space: nowrap;
  background-color: var(--a-color);
  color: var(--background-color);
  border-radius: var(--space-xs);
  transition: background-color var(--transition-base);
}
.post-preview footer a:hover,
.post-preview footer a:focus {
  background-color: var(--a-color-hover);
  color: var(--background-color);
}

@media screen and (min-width: 768px) {
  .post-preview {
    display: flex;
    flex-direction: row;
    padding: 0;
  }

  .post-preview-cover {
    flex: 0 0 280px;
    margin: 0;
    border-radius: var(--space-xs) 0 0 var(--space-xs);
    align-self: stretch;
  }

  .post-preview-cover img {
    height: 100%;
    aspect-ratio: auto;
    border-radius: var(--space-xs) 0 0 var(--space-xs);
  }

  .post-preview-body {
    flex: 1;
    padding: var(--space-md);
    display: flex;
    flex-direction: column;
  }

  .excerpt {
    -webkit-line-clamp: 2;
  }

  .post-preview footer {
    margin-top: auto;
  }

  .post-preview h2 {
    font-size: var(--font-size-xl);
  }
}

@media screen and (min-width: 1024px) {
  .post-preview-cover {
    flex: 0 0 320px;
  }

  .post-preview-body {
    padding: var(--space-lg);
  }

  .post-preview h2 {
    font-size: var(--font-size-2xl);
  }
}
</style>
