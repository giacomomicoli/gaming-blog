# Frontend Architecture

> Authoritative reference for AI agents and developers. This document describes the current
> implementation of the frontend. Do not deviate from these patterns, component structures,
> naming conventions, or styling approaches when making changes.

## Structure

```
frontend/
├── app.vue                      # Root: NuxtLoadingIndicator + NuxtLayout + NuxtPage + site-wide WebSite JSON-LD
├── nuxt.config.ts               # SSR, theme loading, i18n, runtime config, transitions, meta
├── locales/
│   ├── it.json                  # Italian UI translations
│   └── en.json                  # English UI translations
├── layouts/
│   └── default.vue              # Header (NavBar) + main slot + footer
├── components/
│   ├── NavBar.vue               # Site navigation with categories dropdown and language switcher
│   ├── PostCard.vue             # Blog post preview card
│   ├── PostMeta.vue             # Post metadata (date, author, category, tags)
│   ├── HeroCarousel.vue         # Featured posts carousel
│   └── TableOfContents.vue      # Sticky heading navigation sidebar
├── pages/
│   ├── index.vue                # Root redirect to /{defaultLocale}
│   └── [lang]/
│       ├── index.vue            # Homepage: hero carousel + post grid
│       ├── blog/[slug].vue      # Full post with content + TOC sidebar
│       ├── category/[name].vue  # Posts filtered by category
│       ├── tag/[name].vue       # Posts filtered by tag
│       ├── about-blog.vue       # Static "About This Blog" page
│       └── about-me.vue         # Static "About Me" page
├── composables/
│   ├── useApi.ts                # API client with server/client URL switching
│   └── useSeo.ts                # Shared canonical/meta/JSON-LD helpers
├── types/
│   └── blog.ts                  # TypeScript interfaces: Post, TocEntry, PostList
├── server/routes/
│   ├── rss.xml.ts               # RSS 2.0 feed generation
│   ├── robots.txt.ts            # Runtime robots.txt generation
│   └── sitemap.xml.ts           # XML sitemap generation
├── assets/
│   ├── css/
│   │   ├── main.css             # Global reset, typography, transitions, scrollbar
│   │   └── notion-content.css   # Styles for rendered Notion HTML blocks
│   └── themes/
│       ├── yarb-dark/theme.css  # Dark theme (default)
│       └── yarb-light/theme.css # Light theme
├── public/
│   └── social/default-social-card.png  # Repo-level fallback share image
├── tests/components/
│   ├── PostCard.test.ts
│   ├── PostMeta.test.ts
│   └── TableOfContents.test.ts
├── Dockerfile                   # Multi-stage: node:20-alpine, 3 stages
└── docker-entrypoint.dev.sh     # Dev: runs npm install before starting
```

## Nuxt Configuration

### SSR

SSR is enabled. The frontend renders server-side for SEO, then hydrates on the client.

### Runtime Config

```typescript
runtimeConfig: {
    backendUrl: process.env.BACKEND_URL || 'http://backend:8000',  // server-side only
    public: {
        backendUrl: process.env.NUXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',  // client-side
        siteUrl: process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost:3000',
        defaultLocale: process.env.DEFAULT_LOCALE || 'it',
        supportedLocales: process.env.SUPPORTED_LOCALES || 'it,en',
    }
}
```

In production, `NUXT_PUBLIC_BACKEND_URL` is set to `/api` (relative path) because
Caddy proxies `/api/*` to the backend. The frontend never exposes the backend's internal port.

### i18n (`@nuxtjs/i18n`)

The `@nuxtjs/i18n` module handles locale routing, translations, and locale detection.

- **Strategy**: `prefix` — all locales use URL prefix (`/it/...`, `/en/...`)
- **Default locale**: From `DEFAULT_LOCALE` env var (default: `it`)
- **Supported locales**: Built from `SUPPORTED_LOCALES` env var at build time
- **Browser detection**: Disabled (`detectBrowserLanguage: false`)
- **Locale files**: `frontend/locales/{code}.json` loaded via `langDir` config
- **Lazy loading**: Enabled for locale files

Root `/` redirects to `/{defaultLocale}` via `pages/index.vue`.

### CSS Loading Order

1. Theme file: `~/assets/themes/{NUXT_THEME}/theme.css` (CSS custom properties)
2. Main styles: `~/assets/css/main.css` (global reset, typography, transitions)
3. Notion styles: `~/assets/css/notion-content.css` (rendered Notion block styling)

### App-Level Meta

```typescript
head: {
    charset: 'utf-8',
    viewport: 'width=device-width, initial-scale=1',
    title: 'No Hype, Just Vibe',
    titleTemplate: '%s | No Hype, Just Vibe',
    meta: [{ name: 'description', content: 'No Hype, Just Vibe — A blog powered by Notion' }],
    link: [
        // Google Fonts: Atkinson Hyperlegible Mono
        // RSS feed: /rss.xml
    ]
}
```

The home page overrides `titleTemplate` to empty string so the title is just "No Hype, Just Vibe"
without the suffix.

### Page Transitions

```typescript
pageTransition: { name: 'page', mode: 'out-in' }
```

CSS in `main.css`:
```css
.page-enter-active, .page-leave-active { transition: opacity var(--transition-base); }
.page-enter-from, .page-leave-to { opacity: 0; }
```

`--transition-base` is `250ms cubic-bezier(0.4, 0.0, 0.2, 1)`.

## Root Component (`app.vue`)

```vue
<template>
    <NuxtLoadingIndicator color="var(--a-color)" :height="3" />
    <NuxtLayout>
        <NuxtPage />
    </NuxtLayout>
</template>
```

- Loading indicator: 3px bar at top of page, uses theme accent color
- All pages wrapped in the default layout

## Layout (`layouts/default.vue`)

Structure: `.site` → `.site-header` (NavBar) + `.site-main` (slot) + `.site-footer`.

- `.site` is a flex column with `min-height: 100vh` to push the footer down
- Footer text uses `$t('footer.text', { year })` for i18n support

## Components

### NavBar.vue

Site navigation with responsive mobile/desktop layout and language switcher.

**Structure**: Brand link ("No Hype, Just Vibe") + hamburger toggle (mobile) + menu links + language switcher.

**Menu items**: Home, Categories (dropdown), About This Blog, About Me, Language links.

**State**:
- `menuOpen: ref(false)` — mobile menu visibility
- `dropdownOpen: ref(false)` — categories dropdown visibility

**Data fetching**: Categories fetched via `useAsyncData` with locale-specific key.

**i18n**: All labels use `$t()` for translations. Links are locale-prefixed (`/${locale}/...`).
Language switcher shows available locales (excluding current) as uppercase links.

**Responsive behavior**:
- Mobile: Hamburger icon toggles menu. Menu is vertical. Categories dropdown nested inline.
- Desktop (768px+): Hamburger hidden. Menu is horizontal flex. Dropdown positioned absolute below trigger.

**CSS classes**: `.navbar`, `.navbar-toggle`, `.hamburger`, `.navbar-menu`, `.navbar-link`,
`.dropdown-trigger`, `.dropdown-menu`, `.dropdown-link`, `.navbar-lang`, `.navbar-link-lang`.

### PostCard.vue

Blog post preview card for grid/list layouts.

**Props**: `{ post: Post }`

**Features**: Cover image (16:9, lazy loaded), title link, publication date + author,
excerpt (line-clamped: 3 lines mobile, 2 lines tablet+), category badge, reading time, tag list, "Read More" button.
All text labels use `$t()`, all links are locale-prefixed (`/${locale}/...`).

**Responsive**: Stacked on mobile, side-by-side at 768px (280px fixed image), larger at 1024px (320px image).

**CSS classes**: `.post-preview`, `.post-preview-cover`, `.post-preview-body`, `.excerpt`,
`.post-preview-tags`, `.tag`.

### HeroCarousel.vue

Featured posts carousel/slider.

**Props**: `{ posts: Post[] }`

**Features**: Horizontal scroll snap, real `<img>` cover images with dark gradient overlay,
auto-advance every 6 seconds (respects `prefers-reduced-motion`), dot navigation.

**Hardcoded colors**: White text (`#fff`), overlay gradient (`rgba(0,0,0,0.75)` to transparent),
excerpt text (`rgba(255,255,255,0.85)`). These are intentional — the hero always uses
dark overlay on images regardless of theme.

**CSS classes**: `.hero`, `.hero-track`, `.hero-slide`, `.hero-overlay`, `.hero-content`,
`.hero-title`, `.hero-excerpt`, `.hero-cta`, `.hero-dots`, `.hero-dot`.

### PostMeta.vue

Post metadata display.

**Props**: `{ post: Post }`

**Renders**: Publication date (formatted via `toLocaleDateString(locale.value, ...)`),
author byline (`$t('post.by')`), reading time (`$t('post.minRead')`), category link (locale-prefixed), tag list (locale-prefixed links).

**CSS classes**: `.post-meta`, `.post-meta-top`, `.post-meta-bottom`, `.byline`,
`.reading-time`, `.post-meta-category`, `.post-meta-tags`, `.tag`.

### TableOfContents.vue

Sticky sidebar navigation for post headings.

**Props**: `{ entries: TocEntry[] }`

**Renders**: Only if `entries.length > 0`. Heading text uses `$t('toc.title')` + anchor links.
Level 3 headings are indented relative to level 2.

**CSS classes**: `.toc`, `.toc-title`, `.toc-list`, `.toc-item`, `.toc-level-2`,
`.toc-level-3`, `.toc-link`.

## Pages

### index.vue (Root Redirect)

Redirects to `/{defaultLocale}` using `navigateTo()`.

### [lang]/index.vue (Homepage)

Fetches featured posts (limit 5) and latest posts (paginated, default limit 10) for the current locale.
Shows `HeroCarousel` if featured posts exist. Post grid below with Previous/Next pagination.

SEO: Title overridden to "No Hype, Just Vibe" (no template suffix), canonical tag,
full Open Graph/Twitter metadata, `CollectionPage` JSON-LD, and `BreadcrumbList` JSON-LD.

### [lang]/blog/[slug].vue (Post Detail)

Fetches single post by slug for the current locale. Shows back link, title (h1), `PostMeta`, optional cover image,
rendered HTML content (`v-html` in `.notion-content` div), and `TableOfContents` sidebar.

SEO: Title is post title. Canonical URL, `hreflang` alternates (when `Translation Key`
data exists), Open Graph/Twitter metadata, `BlogPosting` JSON-LD, and `BreadcrumbList`
JSON-LD are rendered server-side. Twitter card is `summary_large_image`.

Layout: Single column on mobile/tablet. Two-column grid (`1fr 240px`) at 1024px+ with
sticky TOC sidebar.

404 handling: `throw createError({ statusCode: 404 })` if post not found.

### [lang]/category/[name].vue and [lang]/tag/[name].vue

Filtered post listings with breadcrumb navigation. Same grid and pagination as homepage.
All API calls include the current locale.

### [lang]/about-blog.vue and [lang]/about-me.vue

Static pages fetched from `/api/pages/about-blog?lang={lang}` and `/api/pages/about-me?lang={lang}`.
Render title + HTML content. 404 if not found. SEO includes canonical URL, social metadata,
`AboutPage` JSON-LD, and breadcrumb markup.

## Composable: useApi.ts

Central API client. Uses `useRuntimeConfig()` to determine base URL:
- Server-side: `config.backendUrl` (`http://backend:8000`)
- Client-side: `config.public.backendUrl` (`http://localhost:8000` or `/api` in prod)

**Exported functions**:

| Function | Endpoint | Returns |
|----------|----------|---------|
| `getPosts(lang, opts?)` | `GET /api/posts?lang={lang}` | `PostList` |
| `getFeaturedPosts(lang, limit?)` | `GET /api/posts?lang={lang}&featured=true` | `PostList` |
| `getPost(lang, slug)` | `GET /api/posts/{slug}?lang={lang}` | `Post` |
| `getCategories(lang)` | `GET /api/categories?lang={lang}` | `string[]` |
| `getTags(lang)` | `GET /api/tags?lang={lang}` | `string[]` |
| `getPage(lang, slug)` | `GET /api/pages/{slug}?lang={lang}` | `StaticPage` |

Uses Nuxt's `$fetch` utility internally.

## TypeScript Interfaces (`types/blog.ts`)

```typescript
interface Post {
    id: string; slug: string; title: string; excerpt: string;
    category: string | null; tags: string[];
    published_date: string | null; cover_image: string | null;
    social_image?: string | null;
    author: string; featured?: boolean; language: string;
    translation_key?: string | null; meta_description?: string | null;
    last_edited_time?: string | null; alternates?: Record<string, string>;
    reading_time?: number; content_html?: string;
    table_of_contents?: TocEntry[];
}

interface TocEntry {
    id: string; text: string; level: number;  // 2 or 3
}

interface PostList {
    posts: Post[]; total: number; page: number; has_more: boolean;
}

interface StaticPage {
    id: string; slug: string; title: string; language: string;
    meta_description?: string | null; social_image?: string | null;
    translation_key?: string | null; last_edited_time?: string | null;
    alternates?: Record<string, string>; content_html: string;
}
```

## Theme System

### Architecture

Themes are directories under `frontend/assets/themes/`. Each contains a `theme.css` file
that defines CSS custom properties on `:root`. The theme is selected at **build time** via
the `NUXT_THEME` environment variable (default: `yarb-dark`).

### Available Themes

- `yarb-dark` — Dark background (#212830), light text (#d1d7e0), blue accent (#478be6)
- `yarb-light` — Light background (#f5f5f5), dark text (#1a1a2e), blue accent (#2563eb)

### Design Tokens

Both themes define identical token names. All components use these tokens — never hardcode
colors (except in HeroCarousel where white-on-dark-overlay is intentional).

**Color tokens**:
- `--background-color` — Page background
- `--surface-color` — Card/surface background
- `--border-color` — Borders
- `--font-color` — Primary text
- `--font-color-muted` — Secondary/dimmed text
- `--a-color` — Links, CTAs, accent elements
- `--a-color-hover` — Link hover state

**Spacing** (8px base unit):
`--space-xs` (8px), `--space-sm` (16px), `--space-md` (24px), `--space-lg` (32px),
`--space-xl` (48px), `--space-2xl` (64px)

**Typography**:
- `--font-family`: `"Atkinson Hyperlegible Mono", monospace`
- Sizes: `--font-size-xs` (0.75rem) through `--font-size-4xl` (2.5rem)
- Line heights: `--line-height-tight` (1.25), `--line-height-base` (1.5), `--line-height-relaxed` (1.625)

**Transitions**:
- `--transition-fast`: 150ms ease
- `--transition-base`: 250ms cubic-bezier(0.4, 0.0, 0.2, 1)

**Layout**:
- `--touch-target-min`: 48px (accessibility)
- Containers: `--container-sm` (640px) through `--container-xl` (1200px)

### Adding a New Theme

1. Create `frontend/assets/themes/{name}/theme.css`
2. Define all CSS custom properties listed above on `:root`
3. Set `NUXT_THEME={name}` in `.env`
4. Rebuild the frontend (`make dev-rebuild` or redeploy)

## CSS Conventions

### Class Naming

BEM-inspired: `.block-element` pattern. No strict BEM modifiers — state is typically
handled with Vue's `:class` binding or data attributes.

Examples: `.post-preview-cover`, `.navbar-menu`, `.hero-slide`, `.toc-level-3`.

### Responsive Breakpoints

- Mobile first (no media query)
- Tablet: `@media (min-width: 768px)`
- Desktop: `@media (min-width: 1024px)`
- Large: `@media (min-width: 1200px)` or `@media (min-width: 1280px)`

### Accessibility

- `@media (prefers-reduced-motion: reduce)` — disables animations and transitions
- `@media (prefers-contrast: high)` — bolder borders
- Print styles: black on white, simplified layout
- Touch targets: minimum 48px (enforced via `--touch-target-min`)
- Focus outlines: `2px solid var(--a-color)` with offset

### Notion Content Styling

`notion-content.css` styles all HTML generated by the backend renderer. Scoped under
`.notion-content` class. Covers paragraphs, headings, lists, code blocks, blockquotes,
callouts, tables, images, embeds, equations, toggles, and all text annotations.

Prose width limited to `var(--container-md)` (768px) at desktop size.

## Server Routes

### RSS Feed (`/rss.xml`)

Fetches up to 50 posts from the backend for the requested locale (via `?lang=` query param).
Generates RSS 2.0 XML with CDATA, `<language>` tag set to the locale code.
Channel title: "No Hype, Just Vibe". Content-Type: `application/rss+xml; charset=utf-8`.

### Sitemap (`/sitemap.xml`)

Generates URLs for all locales. Static pages include `xhtml:link` hreflang alternates when
translation mappings exist. Uses backend `last_edited_time` / `published_date` for `lastmod`.
Paginates through all posts per locale (limit 50 per request). Priorities: homepage 1.0,
about-blog 0.7, about-me 0.6, posts 0.8.

### Robots (`/robots.txt`)

Generated at runtime from `siteUrl` so the sitemap reference stays correct across local,
staging, and production environments.
Content-Type: `application/xml; charset=utf-8`.

## Date Formatting

All dates displayed using locale-aware formatting:
```typescript
new Date(date).toLocaleDateString(locale.value, { year: 'numeric', month: 'long', day: 'numeric' })
```

The `locale.value` comes from `useI18n()` and matches the current URL prefix locale code.

## SEO / Meta Patterns

SEO metadata is centralized in `useSeo.ts`.

- Canonical URLs are emitted on all indexable pages.
- `max-image-preview:large` is applied through the page-level robots meta tag.
- `og:image` / `twitter:image` fall back from page-specific image -> post cover -> repo default social card.
- `application/ld+json` is emitted server-side for `WebSite`, `BlogPosting`, `CollectionPage`, `WebPage` / `AboutPage`, and `BreadcrumbList`.

## i18n (Frontend)

- Use `const { locale, t } = useI18n()` in components to access locale and translations
- All internal links must be locale-prefixed: `/${locale}/blog/${slug}`, `/${locale}/category/${name}`
- All user-visible static text must use `$t('key')` or `t('key')` — no hardcoded strings
- Locale files are in `frontend/locales/{code}.json` — add new keys to all locale files when adding UI text
- Date formatting uses `locale.value` for locale-aware output
- `useAsyncData` keys must include the locale to avoid stale data across locale switches

Cache keys for `useAsyncData` should be descriptive, unique, and include the locale:
- `'posts-{locale}'` — homepage post list
- `'post-{locale}-{slug}'` — individual post
- `'category-{locale}-{name}'` — category page posts
- `'tag-{locale}-{name}'` — tag page posts
- `'featured-posts-{locale}'` — hero carousel data
- `'nav-categories-{locale}'` — navbar categories dropdown

## Dockerfile

Three-stage build:
1. **deps**: Install npm dependencies
2. **builder**: Build Nuxt app (receives `NUXT_THEME` build arg)
3. **runtime**: `node:20-alpine`, runs `.output/server/index.mjs` on port 3000

Dev uses `docker-entrypoint.dev.sh` which runs `npm install` before starting the dev server
(needed because volume mounts wipe node_modules).
