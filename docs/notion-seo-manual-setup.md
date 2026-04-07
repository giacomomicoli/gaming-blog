# Notion SEO Manual Setup

This document explains how to fill SEO-related Notion fields after the SEO foundation work lands in code.

Use `docs/notion-setup.md` for database creation and property setup.
Use this file for editorial conventions, examples, and field-filling rules.

## When To Apply These Changes

Apply the required fields before you expect full multilingual SEO coverage for posts and static pages.

Apply the recommended fields when you want tighter control over snippets and social previews.

## Databases To Update

- `Posts`
- `Pages`

## Required Fields

### Posts

| Property Name | Type | Why it matters |
|---------------|------|----------------|
| `Translation Key` | Rich Text | Links localized versions of the same post so the site can emit reliable `hreflang` alternates |

### Pages

| Property Name | Type | Why it matters |
|---------------|------|----------------|
| `Translation Key` | Rich Text | Links localized versions of the same static page so the site can emit reliable `hreflang` alternates |

## Recommended Fields

### Posts

| Property Name | Type | Why it matters |
|---------------|------|----------------|
| `Meta Description` | Rich Text | Optional SEO description override; falls back to `Excerpt` when empty |

### Pages

| Property Name | Type | Why it matters |
|---------------|------|----------------|
| `Meta Description` | Rich Text | Strongly recommended page description used for snippets, social previews, and page-level structured data |

### Posts And Pages

| Property Name | Type | Why it matters |
|---------------|------|----------------|
| `Social Image` | URL | Overrides the default share image for `og:image`, `twitter:image`, and structured data |

## How To Add A Property In Notion

1. Open the target database.
2. Click the `+` button at the end of the property row.
3. Enter the exact property name from the tables above.
4. Select the property type shown in the tables above.
5. Save the property.

## How To Choose `Translation Key`

`Translation Key` is an internal stable identifier used to connect localized versions of the same content item.

It is not a public URL.
It does not need to be translated.
It must be exactly the same across all language versions of the same post or page.

### If Slugs Are The Same Across Locales

Use the shared slug itself as the `Translation Key`.

Example:

| Language | Slug | Translation Key |
|----------|------|-----------------|
| `it` | `resident-evil-requiem` | `resident-evil-requiem` |
| `en` | `resident-evil-requiem` | `resident-evil-requiem` |

### If Slugs Are Different Across Locales

Pick one stable shared key and reuse it in all locales.

Recommended convention:
use the English slug when it exists, because it is usually stable and easy to read.

Example:

| Language | Slug | Translation Key |
|----------|------|-----------------|
| `it` | `recensione-resident-evil-requiem` | `resident-evil-requiem-review` |
| `en` | `resident-evil-requiem-review` | `resident-evil-requiem-review` |

This is also valid:

| Language | Slug | Translation Key |
|----------|------|-----------------|
| `it` | `recensione-resident-evil-requiem` | `resident-evil-requiem` |
| `en` | `resident-evil-requiem-review` | `resident-evil-requiem` |

The important rule is consistency: every translation of the same content item must share the exact same `Translation Key`.

### Invalid Example

Do not create locale-specific keys.

| Language | Slug | Translation Key |
|----------|------|-----------------|
| `it` | `recensione-resident-evil-requiem` | `resident-evil-requiem-it` |
| `en` | `resident-evil-requiem-review` | `resident-evil-requiem-en` |

These values would not link the two posts together.

### Rules

1. Keep the value stable over time.
2. Reuse the same value only for true translations of the same content.
3. Do not change the `Translation Key` when only one locale slug changes.
4. Do not create locale-specific keys such as `-it` and `-en`.
5. For built-in static pages like `about-blog` and `about-me`, keep the slug identical across locales because the frontend routes are fixed.

## How To Fill `Meta Description`

`Meta Description` should be written per language and per entry.

Good structure:

1. What the content is about.
2. The main angle, verdict, or value.
3. What the reader will get.

### Post Example

EN:

`Resident Evil Requiem is a tense return to survival horror with stronger pacing and a more oppressive atmosphere. Read our spoiler-free review and verdict.`

IT:

`Resident Evil Requiem e un ritorno teso al survival horror, con un ritmo piu solido e un'atmosfera piu opprimente. Leggi la nostra recensione spoiler-free e il verdetto.`

### Static Page Examples

`About Blog` EN:

`No Hype, Just Vibe is an independent gaming and culture blog focused on clear reviews, features, and editorial writing without hype.`

`About Blog` IT:

`No Hype, Just Vibe e un blog indipendente su gaming e cultura, con recensioni, approfondimenti e scrittura editoriale senza hype.`

`About Me` EN:

`Meet FakeJack, the editor behind No Hype, Just Vibe, and learn how the blog approaches criticism, reviews, and gaming culture.`

`About Me` IT:

`Scopri chi e FakeJack, autore di No Hype, Just Vibe, e come il blog affronta critica, recensioni e cultura videoludica.`

### Rules

1. Keep it language-specific.
2. Aim for roughly 140 to 160 characters.
3. Avoid keyword stuffing.
4. Avoid repeating the title word-for-word unless it helps clarity.
5. Make sure it matches the actual content of the page.
6. If `Meta Description` is empty on posts, the site falls back to `Excerpt`, so keep `Excerpt` useful even if you later add `Meta Description`.

## How To Fill `Social Image`

`Social Image` is optional.
Use it only when you want to override the normal image fallback.

Current fallback chain in code:

1. `Social Image`
2. `Cover`
3. default repo social card

### When To Add It

Add `Social Image` if:

1. the cover is missing
2. the cover is too small
3. the cover is too vertical
4. the cover is not representative enough for sharing
5. you want a dedicated branded social card

### Good Example

`https://cdn.example.com/social/resident-evil-requiem-review-1200x630.jpg`

### Localized Example

Use different URLs only if the image itself contains language-specific text.

EN:

`https://cdn.example.com/social/resident-evil-requiem-review-en-1200x630.jpg`

IT:

`https://cdn.example.com/social/resident-evil-requiem-review-it-1200x630.jpg`

### Rules

1. Use a stable, public, absolute `https://` image URL.
2. Prefer an image at least `1200px` wide.
3. Use a representative image for the content.
4. Avoid text-heavy images when possible.
5. Do not rely on temporary or signed Notion file URLs if they expire.
6. Leave the field empty if `Cover` is already a strong social-preview image.

## How These Fields Feed SEO And JSON-LD

Editors do not need to write JSON-LD manually.
The application generates structured data from normal editorial fields.

### Current Mapping

| Notion Field | Used For |
|--------------|----------|
| `Name` | page title, `og:title`, `twitter:title`, JSON-LD `headline` or `name` |
| `Meta Description` | meta description, `og:description`, `twitter:description`, JSON-LD `description` |
| `Excerpt` | fallback description for posts when `Meta Description` is empty |
| page content | fallback description source for static pages when `Meta Description` is empty |
| `Social Image` | `og:image`, `twitter:image`, JSON-LD `image` |
| `Cover` | fallback image when `Social Image` is empty |
| `Published Date` | JSON-LD `datePublished` |
| Notion `last_edited_time` | JSON-LD `dateModified`, sitemap `lastmod` |
| `Author` | JSON-LD `author.name` |
| `Category` | JSON-LD `articleSection` |
| `Tags` | JSON-LD `keywords` |
| `Language` | locale tags, `inLanguage`, localized URL |
| `Translation Key` | `hreflang` alternate URL mapping |

### Example: How A Post Turns Into `BlogPosting`

Example post data in Notion:

- `Name`: `Resident Evil Requiem Review`
- `Meta Description`: `Resident Evil Requiem is a tense return to survival horror with stronger pacing and a more oppressive atmosphere. Read our spoiler-free review and verdict.`
- `Social Image`: `https://cdn.example.com/social/resident-evil-requiem-review-1200x630.jpg`
- `Published Date`: `2026-02-01`
- `Author`: `FakeJack`
- `Category`: `Horror`
- `Tags`: `resident evil`, `review`, `survival horror`
- `Language`: `en`

The app then generates structured data similar to this:

```json
{
  "@context": "https://schema.org",
  "@type": "BlogPosting",
  "headline": "Resident Evil Requiem Review",
  "description": "Resident Evil Requiem is a tense return to survival horror with stronger pacing and a more oppressive atmosphere. Read our spoiler-free review and verdict.",
  "image": [
    "https://cdn.example.com/social/resident-evil-requiem-review-1200x630.jpg"
  ],
  "datePublished": "2026-02-01",
  "dateModified": "2026-02-05T10:00:00.000Z",
  "author": {
    "@type": "Person",
    "name": "FakeJack"
  },
  "articleSection": "Horror",
  "keywords": "resident evil, review, survival horror",
  "inLanguage": "en",
  "mainEntityOfPage": "https://gaming.fakejack.dev/en/blog/resident-evil-requiem-review"
}
```

### Current Structured Data Types

Phase 1 currently generates:

- `WebSite` for the whole site
- `BlogPosting` for blog post pages
- `CollectionPage` for homepage, category pages, and tag pages
- `AboutPage` or `WebPage` for static pages
- `BreadcrumbList` for page hierarchy

You do not need to add a separate JSON-LD field in Notion for this phase.

## Backfill Order

1. Add `Translation Key` to `Posts`.
2. Add `Translation Key` to `Pages`.
3. Backfill all translated entries first.
4. Add `Meta Description` to `Pages`.
5. Optionally add `Meta Description` to posts when `Excerpt` is not strong enough.
6. Add `Social Image` later if you need more control than `cover_image + default fallback`.

## What Happens If Fields Are Missing

- Missing `Translation Key`: the site cannot emit reliable per-page `hreflang` alternates for that item.
- Missing `Meta Description` on posts: the site falls back to the post excerpt.
- Missing `Meta Description` on pages: the site falls back to a summary extracted from the rendered page content.
- Missing `Social Image`: the site falls back to the post cover image, or the repo-level default social card.

## Quick Validation Checklist

After backfilling Notion:

1. Open one translated post in each locale and confirm both entries share the same `Translation Key`.
2. Open one translated static page in each locale and confirm both entries share the same `Translation Key`.
3. Confirm `Meta Description` is filled for `Pages` entries that should rank and index.
4. Confirm any `Social Image` URLs are public and render in the browser without authentication.
5. Rebuild or redeploy if needed, then inspect page source and verify:
   - canonical URL
   - `hreflang` alternates
   - `og:image`
   - `application/ld+json`
