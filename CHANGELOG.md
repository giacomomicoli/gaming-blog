# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.9] - 2026-03-27

### Fixed

#### Infrastructure

- Fix `docker stack deploy` failing with invalid interpolation error: the v1.0.8 Redis
  healthcheck used `$(cat /run/secrets/redis_password)` which Docker Compose treated as a
  variable reference; escape `$` as `$$` so the shell subshell is passed through verbatim
  (the `command:` field already used `$$` correctly)

## [1.0.8] - 2026-03-27

### Security

#### Infrastructure

- Close publicly exposed Redis port (6379) on production server flagged by BSI/CERT-Bund:
  remove host port mapping from base `docker-compose.yml` (Redis only needs internal
  `blog-net` access), move port to `docker-compose.dev.yml` for local development only,
  and add `requirepass` authentication via Docker secret as defense-in-depth

## [1.0.7] - 2026-03-20

### Fixed

#### Infrastructure

- Fix Docker Swarm DNS collision between blog stacks: both stacks define a `backend` service
  on the shared `proxy-net`, causing Docker DNS round-robin between the two backends and
  intermittent SSR 404 errors. Added `blog-api-internal` network alias on `blog-net` and
  changed frontend SSR env from `BACKEND_URL` to `NUXT_BACKEND_URL=http://blog-api-internal:8000`
  (Nuxt 3 only reads `NUXT_`-prefixed env vars at runtime)

## [1.0.6] - 2026-03-19

### Fixed

#### Infrastructure

- Fix v1.0.5 not taking effect: Docker Compose environment merge with empty
  value (`NUXT_PUBLIC_BACKEND_URL=`) did not override the base file's value
  in `docker stack deploy`; moved `NUXT_PUBLIC_BACKEND_URL=http://localhost:8000`
  from base `docker-compose.yml` to `docker-compose.dev.yml` so it only exists
  in the dev environment and is completely absent in production

## [1.0.5] - 2026-03-19

### Fixed

#### Infrastructure

- Fix client-side API requests going to `http://localhost:8000` instead of
  relative `/api/...` in production: the base `docker-compose.yml` sets
  `NUXT_PUBLIC_BACKEND_URL=http://localhost:8000` (for dev), and the prod
  compose never overrode it — Nuxt Nitro injects this at runtime into SSR HTML,
  breaking all client-side navigation (CORS + unreachable host)

## [1.0.4] - 2026-03-19

### Fixed

#### Infrastructure

- Fix deploy workflow failing silently when VPS has local file modifications,
  preventing all code updates from reaching production (`git pull` replaced
  with `git fetch` + `git reset --hard`; added `set -e` for fail-fast)

## [1.0.3] - 2026-03-19

### Fixed

#### Frontend

- Fix client-side API base URL not taking effect in production: change default
  `NUXT_PUBLIC_BACKEND_URL` to empty string so it is baked into the client bundle
  at build time, ensuring relative `/api/...` paths work without runtime override
- Remove unnecessary `NUXT_PUBLIC_BACKEND_URL` env var from production Docker Compose

## [1.0.2] - 2026-03-19

### Fixed

#### Infrastructure

- Fix double `/api` prefix on client-side API requests in production causing 404 errors
  (`NUXT_PUBLIC_BACKEND_URL=/api` + hardcoded `/api/...` paths = `/api/api/...`)

## [1.0.1] - 2026-03-19

### Added

#### Infrastructure

- GitHub Actions CI workflow: lint (ruff), backend tests (pytest), frontend tests (vitest)
  on push/PR to dev, release, main
- GitHub Actions Deploy workflow: build and push Docker images to ghcr.io, deploy to VPS
  via SSH on push to main
- Docker images published to GitHub Container Registry (ghcr.io) with commit SHA tags

### Fixed

#### Frontend

- Fix empty pages on client-side navigation by adding reactive page key to NuxtPage
  and making route params reactive in dynamic pages (blog post, category, tag)
- Fix navbar categories not refreshing on locale switch

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
