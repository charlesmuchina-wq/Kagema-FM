# Contributing to Kagema-FM

Thanks for contributing! This guide is the practical, up-to-date reference for
developing, testing, and shipping changes in this repository. For the condensed
automation-oriented version, see [`CLAUDE.md`](./CLAUDE.md).

---

## 1. Repository layout

| Area | Path | Stack / tooling |
|------|------|-----------------|
| Mobile/web app | `frontend/` | Expo / React Native (TypeScript), **yarn-managed** |
| API & services | `backend/` | Python / FastAPI, linted with **ruff**, tested with **pytest** |
| Monitoring tooling | `scripts/` + root `package.json` | Node (stream-health checks, mirror resolution) |
| CI | `.github/workflows/quality-check.yml` | Enforces the gates in §6 on every PR |

> **Package managers:** the frontend is **yarn** (`yarn.lock`,
> `packageManager: yarn`). Do **not** run `npm install` / `npm ci` there — it
> fails on a peer-dependency conflict (`expo-three` vs `three`). Use `yarn`.

---

## 2. Prerequisites & setup

- **Node** ≥ 20, **Yarn** 1.x (Classic)
- **Python** 3.11
- Frontend deps: `cd frontend && yarn install --frozen-lockfile`
- Backend lint/test tools: `pip install ruff==0.15.8 pytest`

Environment variables live in `.env` files that are **not** committed
(`.gitignore` excludes them). The backend reads `MONGO_URL`, `DB_NAME`, and
optional API keys via `python-dotenv`; the frontend reads
`EXPO_PUBLIC_BACKEND_URL` etc. Never commit secrets.

---

## 3. Monitor app state

| Check | Command |
|-------|---------|
| Radio Browser stream health | `npm test` (root) — runs `scripts/test-streams.js` |
| Stream health behind a proxy | `npm run test:streams` (sets `NODE_USE_ENV_PROXY=1`) |
| Find the fastest healthy mirror | `npm run refresh-stations` |
| Frontend lint | `cd frontend && yarn lint` (or root `npm run lint`) |
| Frontend type-check | `cd frontend && npx tsc --noEmit` |
| Backend lint | `cd backend && ruff check .` (pin `ruff==0.15.8`) |
| Backend unit tests | `cd backend && python -m pytest test_radio_browser_client.py` |
| Dependency audit (frontend) | `cd frontend && yarn npm audit` |

> `scripts/test-streams.js` is a **live network probe**. When outbound access to
> `*.api.radio-browser.info` is blocked (e.g. a restricted CI egress policy) it
> exits `2` — an "API unreachable" signal, **not** a stream failure.

---

## 4. Repair code & streams

- **Frontend lint fixes:** `cd frontend && yarn lint --fix`
- **Backend lint fixes:** `cd backend && ruff check . --fix` (safe fixes only;
  avoid `--unsafe-fixes` without review)
- **Radio Browser access:** use the shared client
  `backend/radio_browser_client.py` (`RadioBrowserClient`) so calls fail over
  across mirrors (`de1 → nl1 → at1 → fi1`) with one descriptive User-Agent.
  **Do not hardcode a single mirror URL.**
- **Broken station URLs / mirror down:** run `npm run refresh-stations`.
- **Dependency vulnerabilities:** remediate through **yarn**, never
  `npm audit fix` (it writes `package-lock.json` and desyncs the authoritative
  `yarn.lock`). Some fixes need breaking major upgrades — do those deliberately,
  with device testing, not automatically.

---

## 5. Commit & open a pull request

Changes reach `main` **only through a reviewed, CI-green pull request** — do
**not** `git push origin main` directly.

1. Branch: `git checkout -b <type>/<short-description>`
2. Stage reviewed changes with explicit paths: `git add <paths>`
   (never commit `.env`, secrets, or `node_modules`)
3. Commit with a [Conventional Commit](https://www.conventionalcommits.org)
   message, e.g.
   `git commit -m "fix(radio): route station lookups through the failover client"`
4. Push: `git push -u origin <branch>`
5. Open a PR into `main` and fill in
   [`.github/PULL_REQUEST_TEMPLATE.md`](./.github/PULL_REQUEST_TEMPLATE.md)

**Conventional Commit types:** `feat`, `fix`, `docs`, `refactor`, `test`,
`style`, `ci`, `chore`, `perf`.

---

## 6. CI gates (must pass before merge)

- **Configuration Validation** — required config files present
- **Frontend Linting** — ESLint, **0 errors** (warnings allowed)
- **Backend Linting** — ruff clean (pinned `0.15.8`)
- **Backend Unit Tests** — pytest
- **Health Check / Monitoring Script Validation** — shell + Node script syntax
- **Security Vulnerability Check**

Advisory (reported, non-gating): TypeScript type-check, Design Token usage, web
build export.

---

## 7. Merging / auto-merge

A PR merges into `main` only after **CI is green** and a **human approves** it
(you may not approve your own PR). To have GitHub merge automatically once both
are satisfied, use **auto-merge**:

**One-time (admin — repo Settings):**
- **Settings → General → Pull Requests → enable "Allow auto-merge".**
- **Settings → Branches:** add a ruleset / protection rule on `main` that
  **requires status checks** (the gating jobs above, or the single
  **Quality Check Summary** job that depends on them) and, for "merge once
  approved", **requires approvals** (e.g. 1).
- Choose an allowed merge method (squash / merge / rebase).

**Per PR:** click **Enable auto-merge** (or `gh pr merge --auto --squash <n>`)
and pick the method. The branch must be conflict-free (`mergeable_state: clean`);
if a base push makes it un-mergeable, merge/rebase `main` in and push.

---

## 8. Observability

The app installs global error handling and lightweight performance timing:

- `frontend/utils/errorTracking.ts` — `captureException` / `captureMessage`,
  global handlers for unhandled errors and promise rejections, and an
  `addReporter` hook (documented Sentry integration point).
- `frontend/components/ErrorBoundary.tsx` — app-level React error boundary with
  a recoverable fallback; wraps the app in `frontend/app/_layout.tsx`.
- `frontend/utils/performanceMonitor.ts` — `startTimer` / `endTimer` /
  `measure()` with slow-operation warnings.

Build UI with `DESIGN_TOKENS` from `frontend/constants/designTokens.ts` — no
hardcoded colors, spacing, or font sizes.

---

## 9. Known open items

- **Dependency remediation** — most `npm audit` findings are transitive
  Expo/Metro build-chain deps; real fixes need a deliberate Expo SDK upgrade on
  a branch with device testing (they must go through **yarn**, not npm).
- **Deeper backend failover adoption** — a few remaining call sites can be moved
  onto `RadioBrowserClient`'s failover once they can be runtime-verified.

---

_Questions or gaps in these instructions? Open an issue or a docs PR._
