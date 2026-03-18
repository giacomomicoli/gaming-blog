"""Blog post API endpoints."""

from fastapi import APIRouter, HTTPException, Query

from src.cache import (
    cache_get,
    cache_set,
    categories_key,
    page_key,
    post_key,
    posts_list_key,
    tags_key,
)
from src.config import settings
from src.notion.client import NotionNotFound, notion_client
from src.notion.renderer import extract_toc, render_blocks

router = APIRouter(prefix="/api")


def _validate_lang(lang: str) -> str:
    """Validate and return the language code, falling back to default."""
    if lang in settings.parsed_locales:
        return lang
    return settings.default_locale


# ── Property extraction helpers ─────────────────────────────


def _get_plain_text(prop: dict) -> str:
    """Extract plain text from a title or rich_text property."""
    ptype = prop.get("type", "")
    items = prop.get(ptype, [])
    if isinstance(items, list):
        return "".join(item.get("plain_text", "") for item in items)
    return ""


def _get_select(prop: dict) -> str | None:
    sel = prop.get("select")
    return sel.get("name") if sel else None


def _get_multi_select(prop: dict) -> list[str]:
    return [opt.get("name", "") for opt in prop.get("multi_select", [])]


def _get_date(prop: dict) -> str | None:
    d = prop.get("date")
    return d.get("start") if d else None


def _get_checkbox(prop: dict) -> bool:
    return prop.get("checkbox", False)


def _get_url(prop: dict) -> str | None:
    return prop.get("url")


def _extract_post_meta(page: dict) -> dict:
    """Extract blog post metadata from a Notion page object."""
    props = page.get("properties", {})
    title = _get_plain_text(props.get("Name", {}))
    slug = _get_plain_text(props.get("Slug", {}))
    excerpt = _get_plain_text(props.get("Excerpt", {}))

    return {
        "id": page.get("id", ""),
        "slug": slug,
        "title": title,
        "excerpt": excerpt,
        "category": _get_select(props.get("Category", {})),
        "tags": _get_multi_select(props.get("Tags", {})),
        "published_date": _get_date(props.get("Published Date", {})),
        "cover_image": _get_url(props.get("Cover", {})),
        "author": _get_plain_text(props.get("Author", {})),
        "featured": _get_checkbox(props.get("Featured", {})),
        "language": _get_select(props.get("Language", {})) or settings.default_locale,
    }


def _estimate_reading_time(blocks: list[dict]) -> int:
    """Estimate reading time in minutes from blocks (~200 words/min)."""

    def count_words(blocks_list: list[dict]) -> int:
        total = 0
        for block in blocks_list:
            btype = block.get("type", "")
            data = block.get(btype, {})
            rich_text = data.get("rich_text", [])
            if isinstance(rich_text, list):
                text = " ".join(item.get("plain_text", "") for item in rich_text)
                total += len(text.split())
            children = block.get("children", [])
            if children:
                total += count_words(children)
        return total

    words = count_words(blocks)
    return max(1, round(words / 200))


# ── Endpoints ───────────────────────────────────────────────


@router.get("/posts")
async def list_posts(
    tag: str | None = Query(None),
    category: str | None = Query(None),
    featured: bool | None = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    lang: str = Query(""),
):
    """List published blog posts with optional filtering."""
    lang = _validate_lang(lang)
    cache_k = posts_list_key(lang=lang, tag=tag, category=category, featured=featured, page=page)
    cached = await cache_get(cache_k)
    if cached:
        return cached

    # Build filter: Published = true, Language = lang
    conditions: list[dict] = [
        {"property": "Published", "checkbox": {"equals": True}},
        {"property": "Language", "select": {"equals": lang}},
    ]
    if tag:
        conditions.append(
            {"property": "Tags", "multi_select": {"contains": tag}},
        )
    if category:
        conditions.append(
            {"property": "Category", "select": {"equals": category}},
        )
    if featured is not None:
        conditions.append(
            {"property": "Featured", "checkbox": {"equals": featured}},
        )

    db_filter = {"and": conditions} if len(conditions) > 1 else conditions[0]
    sorts = [{"property": "Published Date", "direction": "descending"}]

    all_posts: list[dict] = []
    async for page_obj in notion_client.query_database(filter=db_filter, sorts=sorts):
        all_posts.append(_extract_post_meta(page_obj))

    total = len(all_posts)
    start = (page - 1) * limit
    end = start + limit
    paginated = all_posts[start:end]

    result = {
        "posts": paginated,
        "total": total,
        "page": page,
        "has_more": end < total,
    }
    await cache_set(cache_k, result)
    return result


@router.get("/posts/{slug}")
async def get_post(slug: str, lang: str = Query("")):
    """Get a single blog post by slug with rendered HTML content."""
    lang = _validate_lang(lang)
    cache_k = post_key(lang, slug)
    cached = await cache_get(cache_k)
    if cached:
        return cached

    # Find the post by slug and language
    db_filter = {
        "and": [
            {"property": "Published", "checkbox": {"equals": True}},
            {"property": "Slug", "rich_text": {"equals": slug}},
            {"property": "Language", "select": {"equals": lang}},
        ]
    }

    page_obj = None
    async for result in notion_client.query_database(filter=db_filter):
        page_obj = result
        break

    if not page_obj:
        raise HTTPException(status_code=404, detail="Post not found")

    # Fetch blocks and render
    try:
        blocks = await notion_client.get_blocks(page_obj["id"])
    except NotionNotFound:
        raise HTTPException(status_code=404, detail="Post content not found")

    meta = _extract_post_meta(page_obj)
    content_html = render_blocks(blocks)
    toc = extract_toc(blocks)
    reading_time = _estimate_reading_time(blocks)

    result = {
        **meta,
        "content_html": content_html,
        "table_of_contents": toc,
        "reading_time": reading_time,
    }
    await cache_set(cache_k, result)
    return result


@router.get("/categories")
async def list_categories(lang: str = Query("")):
    """List all available categories from published posts."""
    lang = _validate_lang(lang)
    cache_k = categories_key(lang)
    cached = await cache_get(cache_k)
    if cached:
        return cached

    categories: set[str] = set()
    db_filter = {
        "and": [
            {"property": "Published", "checkbox": {"equals": True}},
            {"property": "Language", "select": {"equals": lang}},
        ]
    }
    async for page_obj in notion_client.query_database(filter=db_filter):
        cat = _get_select(page_obj.get("properties", {}).get("Category", {}))
        if cat:
            categories.add(cat)

    result = sorted(categories)
    await cache_set(cache_k, result)
    return result


@router.get("/tags")
async def list_tags(lang: str = Query("")):
    """List all tags used across published posts."""
    lang = _validate_lang(lang)
    cache_k = tags_key(lang)
    cached = await cache_get(cache_k)
    if cached:
        return cached

    tags: set[str] = set()
    db_filter = {
        "and": [
            {"property": "Published", "checkbox": {"equals": True}},
            {"property": "Language", "select": {"equals": lang}},
        ]
    }
    async for page_obj in notion_client.query_database(filter=db_filter):
        for tag in _get_multi_select(page_obj.get("properties", {}).get("Tags", {})):
            tags.add(tag)

    result = sorted(tags)
    await cache_set(cache_k, result)
    return result


# ── Static pages ───────────────────────────────────────────


@router.get("/pages/{page_slug}")
async def get_static_page(page_slug: str, lang: str = Query("")):
    """Get a static page by slug from the Pages database."""
    lang = _validate_lang(lang)
    cache_k = page_key(lang, page_slug)
    cached = await cache_get(cache_k)
    if cached:
        return cached

    if not settings.notion_pages_data_source_id:
        raise HTTPException(status_code=404, detail="Pages database not configured")

    db_filter = {
        "and": [
            {"property": "Slug", "rich_text": {"equals": page_slug}},
            {"property": "Language", "select": {"equals": lang}},
        ]
    }

    page_obj = None
    async for result in notion_client.query_database(
        data_source_id=settings.notion_pages_data_source_id, filter=db_filter
    ):
        page_obj = result
        break

    if not page_obj:
        raise HTTPException(status_code=404, detail="Page not found")

    try:
        blocks = await notion_client.get_blocks(page_obj["id"])
    except NotionNotFound:
        raise HTTPException(status_code=404, detail="Page content not found")

    props = page_obj.get("properties", {})
    title = _get_plain_text(props.get("Name", {}))
    content_html = render_blocks(blocks)

    result = {
        "slug": page_slug,
        "title": title,
        "content_html": content_html,
    }
    await cache_set(cache_k, result)
    return result
