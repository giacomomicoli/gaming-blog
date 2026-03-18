"""Tests for the blog API endpoints."""

from unittest.mock import AsyncMock, PropertyMock, patch

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture(autouse=True)
def _no_cache():
    """Bypass Redis cache for all API tests to avoid event loop conflicts."""
    with (
        patch("src.api.posts.cache_get", new_callable=AsyncMock, return_value=None),
        patch("src.api.posts.cache_set", new_callable=AsyncMock),
    ):
        yield


@pytest.fixture
def client():
    return TestClient(app)


def _make_page(
    page_id: str = "page-1",
    title: str = "Test Post",
    slug: str = "test-post",
    published: bool = True,
    category: str | None = "Tech",
    tags: list[str] | None = None,
    published_date: str | None = "2026-02-01",
    excerpt: str = "An excerpt",
    author: str = "Alice",
    language: str = "it",
) -> dict:
    """Build a mock Notion page object."""
    return {
        "id": page_id,
        "properties": {
            "Name": {"type": "title", "title": [{"plain_text": title}]},
            "Slug": {"type": "rich_text", "rich_text": [{"plain_text": slug}]},
            "Excerpt": {"type": "rich_text", "rich_text": [{"plain_text": excerpt}]},
            "Category": {"type": "select", "select": {"name": category} if category else None},
            "Tags": {
                "type": "multi_select",
                "multi_select": [{"name": t} for t in (tags if tags is not None else ["python"])],
            },
            "Published Date": {
                "type": "date",
                "date": {"start": published_date} if published_date else None,
            },
            "Published": {"type": "checkbox", "checkbox": published},
            "Cover": {"type": "url", "url": None},
            "Author": {"type": "rich_text", "rich_text": [{"plain_text": author}]},
            "Language": {"type": "select", "select": {"name": language}},
        },
    }


async def _mock_query_db(*args, **kwargs):
    """Async generator yielding mock pages."""
    pages = [
        _make_page("p1", "First Post", "first-post", category="Tech", tags=["python", "api"]),
        _make_page("p2", "Second Post", "second-post", category="Gaming", tags=["reviews"]),
    ]
    for p in pages:
        yield p


async def _mock_query_db_empty(*args, **kwargs):
    return
    yield  # make it an async generator


def _mock_blocks():
    return [
        {
            "type": "paragraph",
            "id": "b1",
            "paragraph": {
                "rich_text": [{"plain_text": "Hello world this is a test paragraph with words."}],
                "color": "default",
            },
        },
        {
            "type": "heading_2",
            "id": "h1",
            "heading_2": {
                "rich_text": [{"plain_text": "Section Title"}],
                "color": "default",
            },
        },
    ]


# ── /api/posts ─────────────────────────────────────────────

class TestListPosts:
    @patch("src.api.posts.notion_client")
    def test_list_posts(self, mock_client, client):
        mock_client.query_database = _mock_query_db
        resp = client.get("/api/posts?lang=it")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 2
        assert len(data["posts"]) == 2
        assert data["posts"][0]["slug"] == "first-post"
        assert data["page"] == 1

    @patch("src.api.posts.notion_client")
    def test_list_posts_empty(self, mock_client, client):
        mock_client.query_database = _mock_query_db_empty
        resp = client.get("/api/posts?lang=it")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["posts"] == []

    @patch("src.api.posts.notion_client")
    def test_list_posts_pagination(self, mock_client, client):
        mock_client.query_database = _mock_query_db
        resp = client.get("/api/posts?limit=1&page=1&lang=it")
        data = resp.json()
        assert len(data["posts"]) == 1
        assert data["has_more"] is True

        resp2 = client.get("/api/posts?limit=1&page=2&lang=it")
        data2 = resp2.json()
        assert len(data2["posts"]) == 1
        assert data2["has_more"] is False

    @patch("src.api.posts.notion_client")
    def test_list_posts_filter_by_tag(self, mock_client, client):
        mock_client.query_database = _mock_query_db
        resp = client.get("/api/posts?tag=python&lang=it")
        assert resp.status_code == 200

    @patch("src.api.posts.notion_client")
    def test_list_posts_filter_by_category(self, mock_client, client):
        mock_client.query_database = _mock_query_db
        resp = client.get("/api/posts?category=Tech&lang=it")
        assert resp.status_code == 200

    @patch("src.api.posts.notion_client")
    def test_list_posts_default_lang(self, mock_client, client):
        """Omitting lang falls back to default locale."""
        mock_client.query_database = _mock_query_db
        resp = client.get("/api/posts")
        assert resp.status_code == 200


# ── /api/posts/{slug} ─────────────────────────────────────

class TestGetPost:
    @patch("src.api.posts.notion_client")
    def test_get_post(self, mock_client, client):
        async def mock_query(*args, **kwargs):
            yield _make_page("p1", "First Post", "first-post")

        mock_client.query_database = mock_query
        mock_client.get_blocks = AsyncMock(return_value=_mock_blocks())

        resp = client.get("/api/posts/first-post?lang=it")
        assert resp.status_code == 200
        data = resp.json()
        assert data["slug"] == "first-post"
        assert data["title"] == "First Post"
        assert data["language"] == "it"
        assert "content_html" in data
        assert "table_of_contents" in data
        assert data["reading_time"] >= 1

    @patch("src.api.posts.notion_client")
    def test_get_post_not_found(self, mock_client, client):
        mock_client.query_database = _mock_query_db_empty
        resp = client.get("/api/posts/nonexistent?lang=it")
        assert resp.status_code == 404


# ── /api/categories ────────────────────────────────────────

class TestCategories:
    @patch("src.api.posts.notion_client")
    def test_list_categories(self, mock_client, client):
        mock_client.query_database = _mock_query_db
        resp = client.get("/api/categories?lang=it")
        assert resp.status_code == 200
        data = resp.json()
        assert "Tech" in data
        assert "Gaming" in data
        assert data == sorted(data)


# ── /api/tags ──────────────────────────────────────────────

class TestTags:
    @patch("src.api.posts.notion_client")
    def test_list_tags(self, mock_client, client):
        mock_client.query_database = _mock_query_db
        resp = client.get("/api/tags?lang=it")
        assert resp.status_code == 200
        data = resp.json()
        assert "python" in data
        assert "api" in data
        assert "reviews" in data
        assert data == sorted(data)


# ── /health ────────────────────────────────────────────────

class TestHealth:
    def test_health(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


# ── Property extraction ────────────────────────────────────

class TestPropertyExtraction:
    """Test the helper functions via the API response structure."""

    @patch("src.api.posts.notion_client")
    def test_null_category(self, mock_client, client):
        async def mock_query(*args, **kwargs):
            yield _make_page(category=None)

        mock_client.query_database = mock_query
        resp = client.get("/api/posts?lang=it")
        data = resp.json()
        assert data["posts"][0]["category"] is None

    @patch("src.api.posts.notion_client")
    def test_empty_tags(self, mock_client, client):
        async def mock_query(*args, **kwargs):
            yield _make_page(tags=[])

        mock_client.query_database = mock_query
        resp = client.get("/api/posts?lang=it")
        data = resp.json()
        assert data["posts"][0]["tags"] == []

    @patch("src.api.posts.notion_client")
    def test_featured_filter(self, mock_client, client):
        mock_client.query_database = _mock_query_db
        resp = client.get("/api/posts?featured=true&lang=it")
        assert resp.status_code == 200

    @patch("src.api.posts.notion_client")
    def test_null_date(self, mock_client, client):
        async def mock_query(*args, **kwargs):
            yield _make_page(published_date=None)

        mock_client.query_database = mock_query
        resp = client.get("/api/posts?lang=it")
        data = resp.json()
        assert data["posts"][0]["published_date"] is None

    @patch("src.api.posts.notion_client")
    def test_language_in_response(self, mock_client, client):
        async def mock_query(*args, **kwargs):
            yield _make_page(language="en")

        mock_client.query_database = mock_query
        resp = client.get("/api/posts?lang=en")
        data = resp.json()
        assert data["posts"][0]["language"] == "en"


# ── /api/pages/{page_slug} ────────────────────────────────

def _make_static_page(
    page_id: str = "page-1",
    title: str = "About",
    slug: str = "about-blog",
    language: str = "it",
) -> dict:
    """Build a mock Notion page object for the Pages database."""
    return {
        "id": page_id,
        "properties": {
            "Name": {"type": "title", "title": [{"plain_text": title}]},
            "Slug": {"type": "rich_text", "rich_text": [{"plain_text": slug}]},
            "Language": {"type": "select", "select": {"name": language}},
        },
    }


class TestStaticPages:
    @patch("src.api.posts.settings")
    @patch("src.api.posts.notion_client")
    def test_get_about_blog_page(self, mock_client, mock_settings, client):
        async def mock_query(*args, **kwargs):
            yield _make_static_page("page-abc", "About This Blog", "about-blog")

        mock_settings.notion_pages_data_source_id = "ds-pages-123"
        mock_settings.parsed_locales = ["it", "en"]
        mock_settings.default_locale = "it"
        mock_client.query_database = mock_query
        mock_client.get_blocks = AsyncMock(return_value=_mock_blocks())

        resp = client.get("/api/pages/about-blog?lang=it")
        assert resp.status_code == 200
        data = resp.json()
        assert data["slug"] == "about-blog"
        assert data["title"] == "About This Blog"
        assert "content_html" in data

    @patch("src.api.posts.settings")
    @patch("src.api.posts.notion_client")
    def test_get_about_me_page(self, mock_client, mock_settings, client):
        async def mock_query(*args, **kwargs):
            yield _make_static_page("page-def", "About Me", "about-me")

        mock_settings.notion_pages_data_source_id = "ds-pages-123"
        mock_settings.parsed_locales = ["it", "en"]
        mock_settings.default_locale = "it"
        mock_client.query_database = mock_query
        mock_client.get_blocks = AsyncMock(return_value=_mock_blocks())

        resp = client.get("/api/pages/about-me?lang=it")
        assert resp.status_code == 200
        data = resp.json()
        assert data["slug"] == "about-me"
        assert data["title"] == "About Me"

    @patch("src.api.posts.settings")
    @patch("src.api.posts.notion_client")
    def test_get_page_slug_not_found(self, mock_client, mock_settings, client):
        mock_settings.notion_pages_data_source_id = "ds-pages-123"
        mock_settings.parsed_locales = ["it", "en"]
        mock_settings.default_locale = "it"
        mock_client.query_database = _mock_query_db_empty

        resp = client.get("/api/pages/nonexistent?lang=it")
        assert resp.status_code == 404

    @patch("src.api.posts.settings")
    def test_get_page_database_not_configured(self, mock_settings, client):
        mock_settings.notion_pages_data_source_id = ""
        mock_settings.parsed_locales = ["it", "en"]
        mock_settings.default_locale = "it"
        resp = client.get("/api/pages/about-blog?lang=it")
        assert resp.status_code == 404

    @patch("src.api.posts.settings")
    @patch("src.api.posts.notion_client")
    def test_get_page_blocks_not_found(self, mock_client, mock_settings, client):
        from src.notion.client import NotionNotFound

        async def mock_query(*args, **kwargs):
            yield _make_static_page("page-abc", "About", "about-blog")

        mock_settings.notion_pages_data_source_id = "ds-pages-123"
        mock_settings.parsed_locales = ["it", "en"]
        mock_settings.default_locale = "it"
        mock_client.query_database = mock_query
        mock_client.get_blocks = AsyncMock(side_effect=NotionNotFound(404, "not_found", "Not found"))

        resp = client.get("/api/pages/about-blog?lang=it")
        assert resp.status_code == 404
