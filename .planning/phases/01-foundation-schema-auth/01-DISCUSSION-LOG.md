# Phase 1: Foundation, Schema & Auth - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-12
**Phase:** 1-Foundation, Schema & Auth
**Areas discussed:** Login & Registration UI, Post-Login Landing, DB Schema & Seed Data, Docker & Dev Environment

---

## Login & Registration UI

### "Masuk Sebagai" role selector on login

| Option | Description | Selected |
|--------|-------------|----------|
| Remove it | Login form is just email + password. Simpler, matches the PRD's auth endpoint exactly, and avoids a UI element that implies a choice the backend ignores. | ✓ |
| Keep, cosmetic only | Keep the toggle for visual fidelity to the mockup, but its value is never sent to the backend — role is always read from `pengguna.peran` after login. | |
| You decide | Claude picks based on what's cleanest to implement. | |

**User's choice:** Remove it (recommended)

### Registration form layout

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse login card layout | Same card/spacing/input styling as the login mockup, with a Nama field added above Email. Matches the Biblio design system without a new design pass. | ✓ |
| Fuller design pass | More elaborate form — e.g. confirm-password field, terms acknowledgment — needing its own layout decisions beyond the login card. | |
| You decide | Claude designs it following the Biblio design system conventions. | |

**User's choice:** Reuse login card layout (recommended)

### Login ↔ Register navigation

| Option | Description | Selected |
|--------|-------------|----------|
| Separate routes | /login and /register as distinct pages, linked via the 'Daftar sekarang' / 'Sudah punya akun?' links — matches the mockup's link and is simplest with React Router. | ✓ |
| Toggle on same page | Single page component that swaps between login and register forms without a route change. | |
| You decide | Claude picks based on what's simplest to implement. | |

**User's choice:** Separate routes (recommended)

### Post-registration flow

| Option | Description | Selected |
|--------|-------------|----------|
| Auto-login + redirect | Registration endpoint returns a JWT immediately; frontend stores it and lands the user on the authenticated shell — one less step for the user. | ✓ |
| Redirect to login | After registering, the user is sent to the login page and must sign in manually with their new credentials. | |
| You decide | Claude picks based on what's simplest to implement. | |

**User's choice:** Auto-login + redirect (recommended)

---

## Post-Login Landing

### Authenticated shell scope

| Option | Description | Selected |
|--------|-------------|----------|
| Build shell now, placeholders later | Build the persistent header/nav matching the mockups (Katalog, Pinjaman, Dashboard, Anggota) now as a reusable layout. Links to pages that don't exist yet show a 'Coming soon' placeholder. Later phases fill in real content. | ✓ |
| Minimal welcome page only | Phase 1 ships just a bare landing page (welcome + logout). The header/nav shell gets built incrementally as each later phase needs it. | |
| You decide | Claude picks based on what sets up later phases best. | |

**User's choice:** Build shell now, placeholders later (recommended)

### Landing route content

| Option | Description | Selected |
|--------|-------------|----------|
| Simple welcome card | Centered card: 'Selamat datang, {nama}' + role badge + logout button, styled per the Biblio design system. Same for both roles, just the badge differs. | ✓ |
| Role-specific stub sections | Mahasiswa sees a stub 'Pinjaman Saya' section, pustakawan sees stub dashboard cards — more visual scaffolding for later phases to flesh out. | |
| You decide | Claude picks based on what's simplest while still satisfying 'role-appropriate authenticated view'. | |

**User's choice:** Simple welcome card (recommended)

### Session expiry handling

| Option | Description | Selected |
|--------|-------------|----------|
| Auto-redirect to /login on 401 | A frontend API interceptor catches any 401 response, clears the stored token, and redirects to /login (optionally with a 'session expired' message). | ✓ |
| No special handling in Phase 1 | User just sees a failed request/error until they manually go back to /login. Simplest, defer polish to later. | |
| You decide | Claude picks based on what's simplest to implement correctly. | |

**User's choice:** Auto-redirect to /login on 401 (recommended)

### JWT storage location

| Option | Description | Selected |
|--------|-------------|----------|
| localStorage | Simplest for a course-timeline SPA; token persists across page refreshes. Standard approach for this kind of project despite XSS caveats. | ✓ |
| In-memory only (React state/context) | More secure (not accessible to injected scripts), but the user is logged out on every page refresh — likely annoying during dev/demo. | |
| You decide | Claude picks based on FastAPI/React best practices for this timeline. | |

**User's choice:** localStorage (recommended)

---

## DB Schema & Seed Data

### Migration approach

| Option | Description | Selected |
|--------|-------------|----------|
| Alembic migrations | Standard for FastAPI + SQLAlchemy. The 4-person team runs `alembic upgrade head` to apply schema changes without losing local data — useful since 5 phases may touch the schema. | ✓ |
| Plain SQL init script | A .sql file mounted into docker-entrypoint-initdb.d, run once on first Postgres container start. Simpler, but any schema change requires `docker-compose down -v` (wipes data). | |
| You decide | Claude picks based on FastAPI best practices for this timeline. | |

**User's choice:** Alembic migrations (recommended)

### Schema scope for Phase 1

| Option | Description | Selected |
|--------|-------------|----------|
| Full schema now | All 4 tables, FKs, and ENUMs created in Phase 1's migration — matches the roadmap's 'full DB schema' framing. Phases 2-5 only add application code, never table-creation migrations. | ✓ |
| Schema per phase | Phase 1 creates only pengguna + PERAN_PENGGUNA; buku/salinan_buku added in Phase 2, peminjaman in Phase 3. Each migration scoped to what that phase actually uses. | |
| You decide | Claude picks based on what reduces migration churn across phases. | |

**User's choice:** Full schema now (recommended)

### Seed data scope

| Option | Description | Selected |
|--------|-------------|----------|
| Pustakawan test account only | One seeded pustakawan account (e.g. pustakawan@biblio.ac.id) with a documented password, so the team can log in and test the pustakawan role immediately. Keeps Phase 1 focused on auth. | ✓ |
| Pustakawan account + sample catalog | Also seed a handful of buku/salinan_buku rows now, so Phase 2's catalog has real data to display from day one. | |
| You decide | Claude picks based on what's useful for testing Phase 1's own scope. | |

**User's choice:** Pustakawan test account only (recommended)

### Registration password validation

| Option | Description | Selected |
|--------|-------------|----------|
| Minimum 8 characters | Simple length check on the backend — shows basic security awareness for grading without building a full complexity-rule UI. | ✓ |
| No validation | Accept any non-empty password; bcrypt hashes it regardless of strength. Simplest possible. | |
| You decide | Claude picks a sensible minimum. | |

**User's choice:** Minimum 8 characters (recommended)

---

## Docker & Dev Environment

### Dev mode vs production build

| Option | Description | Selected |
|--------|-------------|----------|
| Hot-reload dev mode | Source mounted as volumes; uvicorn --reload for backend, Vite dev server for frontend. Code changes apply instantly — fastest iteration for a 4-week team. | ✓ |
| Production build | Multi-stage Dockerfiles producing optimized bundles, frontend served via nginx. Closer to a real deploy, but rebuild needed after every change. | |
| You decide | Claude picks based on what's standard for FastAPI + React + Docker dev setups. | |

**User's choice:** Hot-reload dev mode (recommended)

### Secrets configuration

| Option | Description | Selected |
|--------|-------------|----------|
| .env + .env.example | docker-compose reads from a gitignored .env file; a committed .env.example documents required variables with placeholder/default values so the team can copy-and-fill. | ✓ |
| Hardcoded defaults in docker-compose.yml | Simplest — fine since this is a course project with no real user data, but less aligned with standard practice. | |
| You decide | Claude picks based on standard practice for this kind of project. | |

**User's choice:** .env + .env.example (recommended)

### Auto-migrate & seed on startup

| Option | Description | Selected |
|--------|-------------|----------|
| Auto-run on startup | Backend container entrypoint runs `alembic upgrade head` then an idempotent seed script before starting uvicorn. `docker-compose up` alone gets the team to a fully working, login-ready app. | ✓ |
| Manual step | After `docker-compose up`, the team runs `docker-compose exec backend alembic upgrade head` and a seed command separately. | |
| You decide | Claude picks based on what best satisfies DEPLOY-01. | |

**User's choice:** Auto-run on startup (recommended)

### Frontend ↔ backend API routing

| Option | Description | Selected |
|--------|-------------|----------|
| Dev proxy + relative /api paths | Frontend code calls /api/..., Vite dev server proxies those to the backend container. Same relative paths work whether running locally or in docker — no CORS configuration needed. | ✓ |
| Absolute URL + CORS | Frontend calls a full URL (e.g. http://localhost:8000/api) via an env var; FastAPI's CORSMiddleware is configured to allow the frontend's origin. | |
| You decide | Claude picks based on what's simplest to configure correctly. | |

**User's choice:** Dev proxy + relative /api paths (recommended)

---

## Claude's Discretion

- Exact ports for backend/frontend/Postgres containers
- Specific seeded pustakawan credentials (to be documented for the team)
- FastAPI/React project folder structure and naming conventions
- JWT payload contents (must carry at least user id + role)
- Exact wording/styling of "Coming soon" placeholder pages

## Deferred Ideas

None — discussion stayed within Phase 1 scope.
