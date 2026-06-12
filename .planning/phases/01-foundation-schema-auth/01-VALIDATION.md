---
phase: 01
slug: foundation-schema-auth
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-06-12
---

# Phase 01 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (backend, primary); no frontend test framework mandated for Phase 1 |
| **Config file** | none — Wave 0 installs `backend/pytest.ini` (or `pyproject.toml [tool.pytest.ini_options]`) |
| **Quick run command** | `pytest backend/tests/ -x` |
| **Full suite command** | `pytest backend/tests/` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest backend/tests/ -x` (for backend auth/schema tasks); manual browser check for UI tasks
- **After every plan wave:** Run `pytest backend/tests/` (full backend suite)
- **Before `/gsd-verify-work`:** Full backend suite green + manual `docker-compose up` smoke test + manual 375px responsive check
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | 0 | AUTH-01 | V2/V5/V6 | Register mahasiswa (email+password, ≥8 chars), bcrypt hash stored, duplicate email rejected, `peran` hardcoded to `mahasiswa` | integration | `pytest backend/tests/test_auth.py::test_register -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 0 | AUTH-02 | V3 | Login returns JWT valid 1 hour | integration | `pytest backend/tests/test_auth.py::test_login_returns_jwt -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 0 | AUTH-03 | V6 | Password stored as bcrypt hash (`pengguna.kata_sandi` starts with `$2`, never plaintext) | integration | `pytest backend/tests/test_auth.py::test_password_is_hashed -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | 0 | AUTH-04 | V4 | Protected endpoint returns 401 for missing/expired/invalid token | integration | `pytest backend/tests/test_auth.py::test_protected_endpoint_401 -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | — | DEPLOY-01 | — | `docker-compose up` starts db/backend/frontend containers; login page loads | manual / smoke | manual: `docker compose up` then open `http://localhost:5173` | ❌ W0 (manual-only) | ⬜ pending |
| TBD | TBD | — | NFR-01 | — | API responses complete in <2s | manual | manual: `curl -w "%{time_total}" ...` against `/api/autentikasi/masuk` | ❌ W0 (manual-only) | ⬜ pending |
| TBD | TBD | — | NFR-02 | — | Login/register/shell render correctly at 375px width | manual / visual | manual: browser devtools resize to 375px | ❌ W0 (manual-only) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

*Task ID / Plan / Wave columns are TBD — to be filled once PLAN.md files assign concrete task IDs.*

---

## Wave 0 Requirements

- [ ] `backend/tests/conftest.py` — pytest fixtures: test DB session (throwaway Postgres schema or SQLite in-memory), FastAPI `TestClient`
- [ ] `backend/tests/test_auth.py` — stubs/tests for AUTH-01, AUTH-02, AUTH-03, AUTH-04
- [ ] `backend/pytest.ini` (or `pyproject.toml [tool.pytest.ini_options]`) — pytest config
- [ ] Framework install: add `pytest`, `httpx` to `requirements-dev.txt` (httpx required for FastAPI `TestClient`)
- [ ] No frontend automated test framework planned for Phase 1 — D-01..D-08 UI behaviors rely on manual verification

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| `docker-compose up` starts all 3 containers and login page loads | DEPLOY-01 | No Docker/automated container runtime available in this environment; this is an environment-level smoke test | Run `docker compose up`, wait for healthy containers, open `http://localhost:5173` in a browser, confirm the login page renders |
| API responses complete in <2s | NFR-01 | No load-testing tooling mandated for a course project at this scale; trivially met by current scope | Time a sample request, e.g. `curl -w "%{time_total}\n" -o /dev/null -s -X POST http://localhost:8000/api/autentikasi/masuk -d '...'`, confirm < 2s |
| Login, register, and authenticated shell render correctly at 375px | NFR-02 | Visual/responsive layout check, not unit-testable | Open browser devtools, set viewport to 375px width, visually verify `/login`, `/register`, and the authenticated shell render without overflow/clipping per 01-UI-SPEC.md |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
