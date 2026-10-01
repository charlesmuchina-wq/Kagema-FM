# Kagema-FM — Developer Instructions

This repository is a radio-streaming app:

- **`frontend/`** — Expo / React Native (TypeScript), **yarn-managed** (`yarn.lock`,
  `packageManager: yarn`). Do **not** use `npm install`/`npm ci` here — it fails on
  a peer-dependency conflict; use yarn.
- **`backend/`** — Python / FastAPI. Linted with **ruff**, tested with **pytest**.
- **`scripts/`** + repo-root **`package.json`** — Node monitoring tooling for the
  Radio Browser API (stream-health checks, mirror resolution).

CI (`.github/workflows/quality-check.yml`) enforces the gates below on every PR.

---

## 1. Monitor app state

| Check | Command |
|-------|---------|
| Radio Browser stream health | `npm test` (root) — runs `scripts/test-streams.js` |
| Stream health behind a proxy | `npm run test:streams` (sets `NODE_USE_ENV_PROXY=1`) |
| Find a working mirror | `npm run refresh-stations` |
| Frontend lint | `cd frontend && yarn lint` (or root `npm run lint`) |
| Frontend type-check | `cd frontend && npx tsc --noEmit` |
| Backend lint | `cd backend && ruff check .` (pin `ruff==0.15.8`) |
| Backend unit tests | `cd backend && python -m pytest test_radio_browser_client.py` |
| Dependency audit (frontend) | `cd frontend && yarn npm audit` |

Note: `scripts/test-streams.js` is a **live network probe**. When outbound access
to `*.api.radio-browser.info` is blocked (e.g. a restricted CI egress policy) it
exits `2` — that is an "API unreachable" signal, not a stream failure.

## 2. Repair code & streams

- **Frontend lint fixes:** `cd frontend && yarn lint --fix`.
- **Backend lint fixes:** `cd backend && ruff check . --fix` (safe fixes only; avoid
  `--unsafe-fixes` without review).
- **Radio Browser access:** use the shared client `backend/radio_browser_client.py`
  (`RadioBrowserClient`) so calls fail over across mirrors (`de1 → nl1 → at1 → fi1`)
  with one descriptive User-Agent. Do **not** hardcode a single mirror URL.
- **Broken station URLs / mirror down:** run `npm run refresh-stations` to find the
  fastest healthy mirror.
- **Dependency vulnerabilities:** remediate through **yarn**, never `npm audit fix`
  (it writes `package-lock.json` and desyncs the authoritative `yarn.lock`). Some
  fixes require breaking major upgrades — do those deliberately, not automatically.

## 3. Commit & open a pull request

Changes reach `main` **only through a reviewed, CI-green pull request** — do **not**
`git push origin main` directly.

1. Work on a feature branch: `git checkout -b <type>/<short-description>`.
2. Stage reviewed changes: `git add <paths>` (prefer explicit paths; never commit
   `.env`, secrets, or `node_modules`).
3. Commit with a Conventional Commit message, e.g.
   `git commit -m "fix(radio): route station lookups through the failover client"`.
4. Push the branch: `git push -u origin <branch>`.
5. Open a PR into `main` and fill in `.github/PULL_REQUEST_TEMPLATE.md`.

## 4. Merging / auto-merge

A PR merges into `main` only after **CI is green** and a **human approves** it
(you may not approve your own PR). To have GitHub merge it for you the moment
those are satisfied, use **auto-merge**:

Prerequisites (one-time, admin — repo Settings):

- **Settings → General → Pull Requests → enable "Allow auto-merge".**
- **Settings → Branches**: add a protection rule / ruleset on `main` that
  **requires status checks** (the gating jobs below, or the single
  **Quality Check Summary** job that depends on them) and, for "merge once
  approved", **requires approvals** (e.g. 1).
- Choose an allowed merge method (squash / merge / rebase).

Per PR:

- Enable auto-merge on the PR (the "Enable auto-merge" button, or
  `gh pr merge --auto --squash <n>`) and pick the merge method. GitHub then
  merges automatically once every required check passes and the required review
  approvals are in — no manual merge click.
- The branch must be conflict-free (`mergeable_state: clean`); if a base push
  makes it un-mergeable, merge/rebase `main` in and push.

## CI gates (must pass before merge)

- **Configuration Validation** — required config files present
- **Frontend Linting** — ESLint, **0 errors** (warnings allowed)
- **Backend Linting** — ruff clean (pinned `0.15.8`)
- **Backend Unit Tests** — pytest
- **Health Check / Monitoring Script Validation** — shell + Node script syntax
- **Security Vulnerability Check**

Advisory (reported, non-gating): TypeScript type-check, Design Token usage, web
build export.
