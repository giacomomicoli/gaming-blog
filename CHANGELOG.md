# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

#### Infrastructure

- GitHub Actions CI workflow: lint (ruff), backend tests (pytest), frontend tests (vitest)
  on push/PR to dev, release, main
- GitHub Actions Deploy workflow: build and push Docker images to ghcr.io, deploy to VPS
  via SSH on push to main
- Docker images published to GitHub Container Registry (ghcr.io) with commit SHA tags

### Changed

#### Infrastructure

- Docker Compose image names changed from local (`blog-backend:latest`) to registry
  (`ghcr.io/giacomomicoli/gaming-blog/backend:${IMAGE_TAG:-latest}`)
- `deploy.sh` updated for manual/emergency use only (removed build step, added
  `--with-registry-auth` flag)

## [1.0.0] - 2026-03-19

### Added

#### Backend (Python / FastAPI)

- Notion-powered CMS with async API client targeting Notion API v2025-09-03
- REST API endpoints: post listing with pagination/filtering, single post retrieval,
  categories, tags, static pages, cache invalidation, and health check
- Notion-to-HTML renderer supporting 20+ block types with rich text formatting
- Table of contents extraction and reading time estimation
- Redis cache layer with cache-first pattern, structured keys (`blog:{lang}:{type}:{id}`),
  configurable TTL, and pattern-based invalidation
- Background sync loop polling Notion for recently edited posts and auto-invalidating cache
- Token-bucket rate limiter with exponential backoff and retry on 429 responses
- Dual Notion database support for blog posts and static pages
- Pydantic Settings configuration with `.env` and Docker Secrets support
- Multi-locale support with configurable `SUPPORTED_LOCALES` and `DEFAULT_LOCALE`
- pytest test suite with fakeredis isolation and mocked Notion client

#### Frontend (Nuxt 3 / Vue 3 / TypeScript)

- Pages: home (hero carousel + post grid), post detail, category listing, tag listing,
  about-blog, about-me
- Components: HeroCarousel, NavBar, PostCard, PostMeta, TableOfContents
- Centralized API composable (`useApi`) with SSR-aware base URL switching
- Internationalization (Italian + English) via `@nuxtjs/i18n` with prefix-based URL strategy
- CSS custom properties design token system with switchable themes (`yarb-dark`, `yarb-light`)
- Dynamic SEO meta tags (Open Graph, Twitter Card) per post
- Mobile-first responsive design with page transitions
- Vitest component tests using `@nuxt/test-utils`

#### Infrastructure

- Docker three-service architecture: backend, frontend, Redis
- Dev environment with Caddy reverse proxy, hot-reload volume mounts
- Production environment with Traefik reverse proxy, HTTPS (Let's Encrypt),
  Docker Swarm deployment, resource limits, and rolling updates
- Automated deploy script with Docker Secrets management
- Makefile for all build, test, lint, and deploy operations
