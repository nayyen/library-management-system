---
phase: 01-foundation-schema-auth
type: skeleton
created: 2026-06-12
---

# Phase 1 — Walking Skeleton

> The thinnest end-to-end slice that proves the full Biblio stack is wired correctly: browser -> Vite proxy -> FastAPI -> PostgreSQL and back. Records the architectural decisions Phases 2-5 build on without renegotiating.

## Phase Goal (User Story)

**As a** mahasiswa or pustakawan, **I want to** register or log in and land on a role-appropriate authenticated shell, **so that** the team has a working full-stack foundation (UI + API + DB, runnable via one command) to add every later feature onto.

## The Skeleton Slice

The smallest thing that exercises every layer end-to-end:

1. `docker compose up` brings up Postgres, FastAPI (uvicorn --reload), and Vite — one command (DEPLOY-01).
2. On startup the backend applies the COMPLETE schema (`alembic upgrade head`) and seeds one pustakawan (real DB write).
3. A user registers a mahasiswa in the browser -> POST /api/autentikasi/registrasi -> bcrypt-hashed row inserted into `pengguna` (real DB write through the full proxy chain).
4. Login -> POST /api/autentikasi/masuk -> credentials verified against `pengguna` (real DB read) -> 1-hour JWT returned.
5. The SPA stores the JWT, renders the authenticated shell with a role badge, and a protected route returns 401 without a valid token (real auth enforcement).

This proves: container orchestration, schema migration, ORM read+write, password hashing, JWT issuance/validation, the Vite->backend proxy, and the React router shell — the spine every later phase reuses.

## Architectural Decisions (binding for Phases 2-5)

| Area | Decision | Source |
|------|----------|--------|
| Backend framework | FastAPI + uvicorn (sync) | PRD / CLAUDE.md |
| ORM | SQLAlchemy 2.x typed declarative (Mapped/mapped_column) | RESEARCH Pattern 1 |
| DB driver | psycopg3 sync (`psycopg[binary]`) — no async this milestone | RESEARCH Alternatives / A6 |
| Migrations | Alembic; initial migration HAND-WRITTEN for PG enum safety (no autogenerate) | D-09, D-10, RESEARCH Pattern 2 / Pitfall 1 |
| Schema scope | COMPLETE schema in Phase 1: 4 tables (pengguna, buku, salinan_buku, peminjaman) + 4 ENUMs (peran_pengguna, kondisi_buku, status_salinan, status_peminjaman) | D-10 |
| Enum naming | lowercase snake_case PG type names (Postgres folds unquoted identifiers) | RESEARCH Open Q1 |
| Password hashing | bcrypt via `pwdlib[bcrypt]` BcryptHasher (NOT passlib) | AUTH-03, RESEARCH Pitfall 2 |
| JWT | PyJWT, HS256, 1-hour exp, payload {sub, peran, nama, exp} | AUTH-02, RESEARCH Pattern 3 |
| Config/secrets | pydantic-settings from gitignored .env; committed .env.example placeholder | D-14 |
| Frontend | React 18 + Vite 5 + react-router v7 (unified package, Data Mode) | RESEARCH Pattern 4 |
| Styling | plain Tailwind v3 (PINNED) + Biblio theme tokens; no shadcn this phase | UI-SPEC, RESEARCH Pitfall 5 |
| HTTP client | axios instance, baseURL "/api", request + 401 response interceptors | D-07, RESEARCH Pattern 5 |
| Token storage | localStorage (XSS tradeoff accepted for course scope) | D-08 |
| Networking | Vite dev proxy /api -> http://backend:8000 (service name); NO CORS middleware | D-16, RESEARCH Pitfall 3/4 |
| Dev orchestration | docker-compose, hot-reload volumes, entrypoint: migrate -> seed -> uvicorn | D-13, D-15, RESEARCH Pattern 6 |

## Directory Layout (established here, reused later)

Backend: `backend/app/{core,models,schemas,routers,dependencies}` + `backend/alembic/versions` + `backend/tests`.
Frontend: `frontend/src/{pages,layouts,components,lib,hooks}` + Tailwind/Vite config at `frontend/` root.
Root: `docker-compose.yml`, `.env.example`, `.gitignore`, `README.md`.

(Full structure in 01-RESEARCH.md "Recommended Project Structure".)

## Build Order

| Plan | Wave | Slice contribution |
|------|------|--------------------|
| 01-01 | 1 | Backend skeleton: complete schema + migration + seed + pydantic config + RED auth tests (DB write proven) |
| 01-02 | 2 | Auth API: bcrypt+JWT, registrasi/masuk/saya, 401 enforcement (turns tests GREEN) |
| 01-03 | 3 | Frontend skeleton: Vite/React/router/Tailwind + auth UI + shell + 401 interceptor (UI interaction proven) |
| 01-04 | 4 | docker-compose orchestration ties all three together (one-command stack) + manual smoke |

## What This Skeleton Does NOT Do (deferred to later phases)

- No catalog, loan, return, or dashboard content — nav routes render "Segera Hadir" placeholders (D-05).
- No sample buku/salinan_buku rows (Phase 2 seeds those).
- No server-side role-gated endpoints yet (Phase 2+ adds pustakawan-only checks via the JWT dependency).
- No rate-limiting, no refresh tokens, no production hardening (course-project dev scope, D-13).
