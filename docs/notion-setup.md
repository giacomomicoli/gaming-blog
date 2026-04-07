# Notion Database Setup

This document describes which databases and properties must exist in your Notion workspace.

Use this file as the structural setup reference.
For detailed guidance on how to fill SEO-related fields such as `Translation Key`, `Meta Description`,
and `Social Image`, see `docs/notion-seo-manual-setup.md`.

## Posts Database

The main database for blog posts.

### Required Properties

| Property Name    | Type         | Description                                    |
|------------------|--------------|------------------------------------------------|
| Name             | Title        | Post title                                     |
| Slug             | Rich Text    | URL-friendly identifier (e.g. `my-first-post`) |
| Excerpt          | Rich Text    | Short summary shown on post cards              |
| Category         | Select       | Single category per post                       |
| Tags             | Multi-select | One or more tags                               |
| Published Date   | Date         | Publication date                               |
| Cover            | URL          | Cover image URL                                |
| Author           | Rich Text    | Author name                                    |
| Published        | Checkbox     | Must be checked for the post to appear on site |
| Featured         | Checkbox     | Check to show post in the homepage hero carousel |
| Language         | Select       | Language code (e.g. `it`, `en`) — each post belongs to one language |

### Recommended SEO Properties

| Property Name    | Type      | Description |
|------------------|-----------|-------------|
| Translation Key  | Rich Text | Shared identifier across localized versions of the same post |
| Social Image     | URL       | Optional override for Open Graph / Twitter previews |
| Meta Description | Rich Text | Optional SEO description override; falls back to Excerpt |

### Adding the Language Property

1. Open your Notion posts database
2. Click **+** to add a new property
3. Set **Name** to `Language` and **Type** to `Select`
4. Add options for each supported locale (e.g. `it`, `en`)
5. Set the `Language` property on each post to its content language

When creating multilingual content, duplicate the post and set each copy to a different language. Each language version should have its own language-specific slug (e.g. `il-mio-post` for Italian, `my-post` for English) for best SEO.

### Adding the Featured Property

1. Open your Notion posts database
2. Click **+** to add a new property
3. Set **Name** to `Featured` and **Type** to `Checkbox`
4. Check the box on any posts you want to appear in the hero carousel

Posts marked as Featured (with a cover image) will rotate in the homepage hero section. If no posts are featured, the hero section is hidden and the page shows the normal post grid.

---

## Pages Database

A separate database for static content pages (About This Blog, About Me, etc.). This is queried by the `GET /api/pages/{slug}` endpoint.

### Required Properties

| Property Name | Type      | Description                                         |
|---------------|-----------|-----------------------------------------------------|
| Name          | Title     | Page title (displayed as the page heading)          |
| Slug          | Rich Text | URL identifier — must match the frontend route slug |
| Language      | Select    | Language code (e.g. `it`, `en`) — same options as Posts |

### Recommended SEO Properties

| Property Name    | Type      | Description |
|------------------|-----------|-------------|
| Translation Key  | Rich Text | Shared identifier across localized versions of the same page |
| Meta Description | Rich Text | SEO description used for snippets and social previews |
| Social Image     | URL       | Optional override for Open Graph / Twitter previews |

### Setup Steps

1. In Notion, create a new **full-page database** (e.g. inside your Blog root page)
2. Name it **"Pages"**
3. Add a **Rich Text** property called `Slug`
4. Add a **Select** property called `Language` with the same locale options as the Posts database
5. Share the database with your integration (same as the Posts database — click **...** → **Add connections** → select your integration)
6. Get the **data source ID** for this database (same process as the Posts database)
7. Set `NOTION_PAGES_DATA_SOURCE_ID` in your `.env` file to this ID

### Creating About Pages

Create entries in the Pages database for each language:

| Name              | Slug        | Language |
|-------------------|-------------|----------|
| About This Blog   | about-blog  | it       |
| About This Blog   | about-blog  | en       |
| About Me          | about-me    | it       |
| About Me          | about-me    | en       |

Then open each entry and write the page content using Notion's editor. The content is rendered to HTML the same way as blog posts (all block types supported).

Keep these built-in page slugs identical across locales because the frontend routes are file-based.

The frontend routes `/{lang}/about-blog` and `/{lang}/about-me` fetch from `/api/pages/about-blog?lang={lang}` and `/api/pages/about-me?lang={lang}` respectively.

### Adding More Pages

You can add any static page by creating a new entry in the Pages database with a unique slug. The backend endpoint `GET /api/pages/{slug}` accepts any slug — just create a matching frontend route.
