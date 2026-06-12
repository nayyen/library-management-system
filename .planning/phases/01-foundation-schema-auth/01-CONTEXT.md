# Phase 1: Foundation, Schema & Auth - Context

**Gathered:** 2026-06-12
**Status:** Ready for planning

<domain>
## Phase Boundary

Stand up the full-stack skeleton for Biblio: `docker-compose` running FastAPI (backend), React (frontend), and PostgreSQL together; the **complete** DB schema (`pengguna`, `buku`, `salinan_buku`, `peminjaman` + all 4 ENUMs) applied via Alembic migrations with seed data; working registration (mahasiswa, email+password) and login (mahasiswa/pustakawan) issuing a 1-hour JWT with bcrypt-hashed passwords; protected-route 401 enforcement; and the login/register UI plus an authenticated shell (header/nav + landing page), responsive down to 375px.

Catalog, loan workflow, returns, and dashboard *content* are out of scope (Phases 2-5) — but the nav shell that will host them is built now.

</domain>

<decisions>
## Implementation Decisions

### Login & Registration UI
- **D-01:** Remove the "Masuk Sebagai" (mahasiswa/pustakawan) role radio from the login form entirely. Login is email + password only — role is read from `pengguna.peran` server-side after authentication, never selected by the user.
- **D-02:** No registration mockup exists. Build `/register` by reusing the login card's layout/styling, adding a `Nama` field above `Email`. Role is fixed to `mahasiswa` — no role picker (matches PROJECT.md: pustakawan accounts are seeded only).
- **D-03:** `/login` and `/register` are separate routes, cross-linked via "Daftar sekarang" (on login) and "Sudah punya akun?" (on register), per the mockup's existing link.
- **D-04:** On successful registration, the backend returns a JWT immediately (auto-login) — frontend stores it and redirects straight to the authenticated shell. No separate "log in after registering" step.

### Post-Login Landing & Session
- **D-05:** Build the persistent authenticated shell (header/nav) now, matching the Stitch mockups' nav structure (Katalog, Pinjaman, Dashboard, Anggota). Routes for pages not yet built (Phases 2-5) render a "Coming soon" placeholder using the shell layout — later phases replace the placeholder, not the shell.
- **D-06:** The Phase 1 landing/home route is a simple centered "Selamat datang, {nama}" welcome card with a role badge (mahasiswa/pustakawan) and a logout button, styled per the Biblio design system. Same layout for both roles — only the badge differs.
- **D-07:** No refresh-token mechanism. A frontend API interceptor catches any 401 response, clears the stored token, and redirects to `/login` (optionally showing a "session expired" message).
- **D-08:** JWT is stored in `localStorage` after login/registration.

### DB Schema & Migrations
- **D-09:** Use Alembic for schema migrations (SQLAlchemy models → Alembic revisions). The team runs `alembic upgrade head` to apply schema changes without wiping local data.
- **D-10:** Phase 1's migration creates the **complete** schema — all 4 tables (`pengguna`, `buku`, `salinan_buku`, `peminjaman`), all FKs, and all 4 ENUMs (`PERAN_PENGGUNA`, `KONDISI_BUKU`, `STATUS_SALINAN`, `STATUS_PEMINJAMAN`) per `docs/PRD.md` §4. Phases 2-5 add application code against this schema — they should not need table-creation migrations.
- **D-11:** Seed data for Phase 1 is **one pustakawan test account** (e.g. `pustakawan@biblio.ac.id` with a documented password) so the team can exercise the pustakawan login/role path immediately. No sample `buku`/`salinan_buku` rows yet — that's Phase 2's concern.
- **D-12:** Registration enforces a minimum password length of 8 characters, validated on the backend.

### Docker & Dev Environment
- **D-13:** `docker-compose up` runs a hot-reload dev setup: source mounted as volumes, `uvicorn --reload` for the backend, Vite dev server for the frontend. Optimized for fast iteration across the 4-week build, not production hardening.
- **D-14:** Secrets (JWT signing key, DB credentials) come from a gitignored `.env`, with a committed `.env.example` documenting required variables and sensible local defaults.
- **D-15:** The backend container's entrypoint runs `alembic upgrade head` and then an idempotent seed script (creates the pustakawan account if missing) before starting `uvicorn`. `docker-compose up` alone produces a fully working, login-ready app — satisfying DEPLOY-01.
- **D-16:** The frontend calls relative `/api/*` paths; the Vite dev server proxies `/api` to the backend container. No CORS configuration needed in either dev or docker-compose.

### Claude's Discretion
- Exact ports for backend/frontend/Postgres containers.
- Specific seeded pustakawan credentials (document wherever chosen — e.g. README — so the team can use them).
- FastAPI/React project folder structure and naming (routers, models, schemas, services; components, pages, hooks).
- JWT payload contents (must at minimum carry user id + role for role-based UI/route decisions).
- Exact wording/styling of "Coming soon" placeholder pages, within the Biblio design system.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Project Requirements & Roadmap
- `.planning/ROADMAP.md` — Phase 1 goal, success criteria, and dependencies
- `.planning/REQUIREMENTS.md` — AUTH-01, AUTH-02, AUTH-03, AUTH-04, DEPLOY-01, NFR-01, NFR-02
- `docs/PRD.md` §4 — full data model (4 tables, 4 ENUMs, FK relationships); §7 — auth endpoint draft (`POST /api/autentikasi/registrasi`, `POST /api/autentikasi/masuk`)

### Design System & Mockups
- `docs/design/stitch_botanical_scholar_library/biblio_design_system/DESIGN.md` — colors, typography (Playfair Display + Inter), spacing, component styles (4px input/button radius, Antique Gold focus states, etc.)
- `docs/design/stitch_botanical_scholar_library/login_biblio/code.html` — login layout reference (remove the role radio per D-01; reuse card/spacing/input styling for `/register` per D-02)
- `docs/design/stitch_botanical_scholar_library/dashboard_pustakawan_biblio/code.html` — header/nav structure reference for the authenticated shell (Katalog, Pinjaman, Dashboard, Anggota links) per D-05

</canonical_refs>

<code_context>
## Existing Code Insights

`backend/` and `frontend/` are currently empty directories — this is a greenfield build with no existing patterns, components, or conventions to reuse. The researcher and planner should establish initial structure from scratch, informed by the canonical refs above.

</code_context>

<specifics>
## Specific Ideas

- The login mockup's "Masuk Sebagai" role radio is a Stitch-generation artifact that doesn't match the PRD's auth flow — explicitly remove it (D-01), don't try to repurpose it.
- The authenticated shell's nav (Katalog, Pinjaman, Dashboard, Anggota) should be built as the reusable layout that Phases 2-5 plug their real pages into — not rebuilt later.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within Phase 1 scope.

</deferred>

---

*Phase: 1-Foundation, Schema & Auth*
*Context gathered: 2026-06-12*
