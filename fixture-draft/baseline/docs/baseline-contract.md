# Workboard Lab — Public Baseline Contract

Version: baseline v1 (frozen for task variants) · Schema version: 1
Status: **public contract**. Everything in this document is normative for the
baseline and for every task built on top of it. Anything not listed here is
**not baseline behavior** — tasks must add it explicitly.

---

## 1. What the baseline is

Workboard Lab is a small, single-user-per-request, local work-item tracker:

- **UI**: React 19 SPA (Vite build), plain CSS, no external assets.
- **API**: Hono HTTP server (`@hono/node-server`), JSON over `/api/*`.
- **Persistence**: one local SQLite file via `better-sqlite3` (WAL mode).
- **Auth**: Better Auth 1.7.18, email+password, cookie sessions
  (`better-auth.session_token`). Better Auth owns the `user`, `session`,
  `account`, `verification` tables. Workboard owns workspace/membership/
  work-item tables. Better Auth's **organization plugin is NOT used**;
  memberships are baseline-owned.
- **No deployment, no hosted services.** The database file is disposable and
  local (`data/` or `.tmp/`, both git-ignored).

## 2. Commands and exit codes

Run from `baseline/`. Node 24.19.0 required (`engines` is set).

| Command | Does | Success exit code |
|---|---|---|
| `npm run dev` | Vite dev UI on :5173 (proxies `/api` to :4310) | runs until stopped |
| `npm run dev:api` | Hono API on :4310, DB `data/workboard.db` | runs until stopped |
| `npm run build` | Vite production build to `dist/` | 0 on success, nonzero on failure |
| `npm run typecheck` | `tsc --noEmit` for app + node tsconfigs | 0 = no type errors |
| `npm run lint` | ESLint (flat config) | 0 = no errors |
| `npm run test:unit` | Vitest, pure domain tests (`tests/unit`) | 0 = all pass |
| `npm run test:api` | Vitest, real-API + real-SQLite integration (`tests/api`) | 0 = all pass |
| `npm run test:e2e` | Playwright, real UI+API+DB on :4599 (`e2e/`) | 0 = all pass |
| `npm run db:reset` | Delete + recreate + seed the DB (env `WORKBOARD_DB`, default `data/workboard.db`); `-- --no-seed` skips seed | 0 on success |
| `npm run check` | typecheck && lint && test:unit && test:api | 0 = all pass |
| `npm run check:full` | `check` && `test:e2e` | 0 = all pass |

Notes:

- `npm run test:e2e` self-contained: its Playwright `webServer` runs
  `npm run build`, resets+seeds `.tmp/e2e.db`, then serves the built SPA and
  API on one origin (127.0.0.1:4599). It may print a transient
  "Database schema mismatch" ERROR line from Better Auth during first-time
  table creation; table creation then succeeds (known 1.7.18 behavior, see
  `docs/source-inventory.json`).
- Exit codes are the tools' own codes (Vitest/Playwright/ESLint/tsc). No
  wrapper swallows failures.
- Environment variables honored by the server and scripts:
  `WORKBOARD_DB` (file path), `WORKBOARD_PORT` (default 4310),
  `WORKBOARD_SERVE_DIST=1` (serve `dist/` + SPA fallback),
  `WORKBOARD_SEED=1` (seed on boot), `WORKBOARD_BASE_URL`,
  `WORKBOARD_TRUSTED_ORIGINS` (comma-separated; the Vite dev origins are
  always trusted).

## 3. Database schema (baseline)

SQLite, WAL mode, `foreign_keys = ON`, `busy_timeout = 5000`. All app DDL is
idempotent (`server/db.ts`). Better Auth's tables are created by Better Auth's
own migration runner on every boot (idempotent).

```sql
workspaces        (id TEXT PK, name TEXT NOT NULL,
                   created_at TEXT NOT NULL, updated_at TEXT NOT NULL)
workspace_members (workspace_id TEXT FK->workspaces ON DELETE CASCADE,
                   user_id TEXT,                -- Better Auth user.id
                   role TEXT CHECK (role IN ('owner','member')),
                   created_at TEXT NOT NULL,
                   PRIMARY KEY (workspace_id, user_id))
work_items        (id TEXT PK,
                   workspace_id TEXT FK->workspaces ON DELETE CASCADE,
                   title TEXT NOT NULL,
                   notes TEXT NOT NULL DEFAULT '',
                   status TEXT CHECK (status IN ('open','in_progress','done')),
                   due_date TEXT,               -- 'YYYY-MM-DD' or NULL
                   version INTEGER NOT NULL DEFAULT 1,
                   created_by TEXT NOT NULL,    -- Better Auth user.id
                   created_at TEXT NOT NULL, updated_at TEXT NOT NULL)
meta              (key TEXT PK, value TEXT NOT NULL)   -- schema_version = 1
```

Conventions:

- All timestamps are ISO-8601 UTC strings (`YYYY-MM-DDTHH:MM:SS.sssZ`).
- `due_date` is a **calendar date string** `YYYY-MM-DD` or NULL. The baseline
  validates the *shape only* (regex); it does **not** verify real calendar
  dates, does not compare dates, and displays the raw string.
- IDs are text: `ws_<20 hex>` / `wi_<20 hex>` (crypto random).
- `version` starts at 1 and is incremented on every successful PATCH.
  The baseline is **last-write-wins**: PATCH never fails because of a
  concurrent edit and no client version hint is accepted. (A task variant is
  expected to change this.)

## 4. Seed data (deterministic)

Created by `npm run db:reset` (or `WORKBOARD_SEED=1`). Fixed IDs and pinned
timestamps; user rows are created through Better Auth (ids are random,
password hashes are per-run). Safe to re-run (idempotent).

**Public test credentials:**

| Email | Password | Name | Memberships |
|---|---|---|---|
| `ada@workboard.test` | `ada-passphrase-01` | Ada Streams | owner of Apollo Launch |
| `bruno@workboard.test` | `bruno-passphrase-02` | Bruno Calder | member of Apollo Launch, owner of Borealis Ops |
| `cleo@workboard.test` | `cleo-passphrase-03` | Cleo Marsh | member of Borealis Ops |

Workspaces: `ws_apollo` "Apollo Launch", `ws_borealis` "Borealis Ops".

Items (13; `updated_at` pinned; API lists `updated_at` DESC, id ASC):

| id | workspace | title | status | due_date | updated_at |
|---|---|---|---|---|---|
| wi_103 | apollo | Prepare demo script | open | – | 2026-11-04T10:15:00.000Z |
| wi_106 | apollo | Fix mobile nav overflow | in_progress | – | 2026-11-04T09:00:00.000Z |
| wi_104 | apollo | Ship onboarding email | done | – | 2026-11-03T16:40:00.000Z |
| wi_102 | apollo | Review pricing copy | in_progress | 2026-11-05 | 2026-11-03T11:30:00.000Z |
| wi_107 | apollo | Write release notes | open | 2026-11-20 | 2026-11-02T15:05:00.000Z |
| wi_105 | apollo | Audit analytics events | open | 2026-12-01 | 2026-11-02T10:00:00.000Z |
| wi_101 | apollo | Draft launch checklist | open | 2026-11-12 | 2026-11-01T14:20:00.000Z |
| wi_108 | apollo | Archive old assets | done | – | 2026-11-01T09:30:00.000Z |
| wi_202 | borealis | Update status page template | in_progress | – | 2026-11-04T08:45:00.000Z |
| wi_205 | borealis | Draft vendor renewal memo | open | 2026-11-28 | 2026-11-03T13:10:00.000Z |
| wi_201 | borealis | Rotate API keys | open | 2026-11-15 | 2026-11-02T09:15:00.000Z |
| wi_203 | borealis | Quarterly access review | open | – | 2026-11-01T16:00:00.000Z |
| wi_204 | borealis | Patch VPN gateway | done | – | 2026-11-01T10:45:00.000Z |

## 5. HTTP API (baseline)

JSON only. Success = resource JSON (+ appropriate status). Errors always use:

```json
{ "error": { "code": "<code>", "message": "<human message>", "fields": { "<field>": "<message>" } } }
```

`fields` only appears for validation errors. Codes: `validation_failed` (400),
`unauthenticated` (401), `not_found` (404), `conflict` (reserved, unused in
baseline), `internal_error` (500). Unknown endpoints → 404 `not_found`.

**Session/ownership rules (normative):**

- Requests without a valid Better Auth session → 401 for every endpoint
  except `GET /api/health` and the Better Auth routes.
- Workspace visibility: a workspace is visible to **members only**. A
  non-member (or unknown workspace id) gets **404**, never 403, so the API
  does not leak workspace existence.
- Mutation rule in the baseline: **any member** may create/update/delete
  items in a workspace they belong to. Only the creator of a workspace
  becomes its owner (role `owner`); the owner role currently grants no extra
  powers (documented gap that task variants may address).
- The baseline **ignores unknown JSON keys** in request bodies.
- Values are stored **verbatim**: titles are NOT trimmed, no length caps
  (beyond SQLite), no real-calendar-date checks on `due_date`.

### Endpoints

| Method & path | Auth | Baseline behavior |
|---|---|---|
| `GET /api/health` | none | `200 {ok:true, name:"workboard-lab", schemaVersion:1, time}` |
| `POST /api/auth/sign-up/email` | none | Better Auth sign-up; body `{name, email, password}`; `200 {token, user}` |
| `POST /api/auth/sign-in/email` | none | Better Auth sign-in; sets `better-auth.session_token` cookie |
| `POST /api/auth/sign-out` | cookie | invalidates session; needs a JSON body (`{}`) |
| `GET /api/me` | cookie | `200 {user:{id,email,name}, workspaces:[{id,name,role,createdAt}]}` (name ASC) |
| `GET /api/workspaces` | cookie | `200 WorkspaceSummary[]` (name ASC) |
| `POST /api/workspaces` | cookie | body `{name}` (non-empty string); `201 WorkspaceDetail` with `role:"owner"` |
| `GET /api/workspaces/:id` | member | `200 WorkspaceDetail` (includes my `role`) |
| `GET /api/workspaces/:id/items` | member | `200 {workspaceId, items: WorkItem[]}` ordered `updated_at DESC, id ASC` |
| `POST /api/workspaces/:id/items` | member | body `{title, notes?, status?, dueDate?}`; defaults `notes:""`, `status:"open"`, `dueDate:null`; `201 WorkItem` |
| `PATCH /api/items/:id` | member | partial `{title?, notes?, status?, dueDate?}`; `dueDate:null` clears; bumps `version`, refreshes `updated_at`; `200 WorkItem`; empty patch `{}` → 400 |
| `DELETE /api/items/:id` | member | `204` no body; item gone from SQLite |

Work-item field rules (baseline): `title` non-empty string (no trim);
`notes` string; `status` ∈ `open | in_progress | done`; `dueDate` `null` or
`YYYY-MM-DD` (shape only). Invalid input → 400 `validation_failed` with a
`fields` map (e.g. `title: "title must be a non-empty string."`).

## 6. UI behavior (baseline)

Single page. States, in order: session check → sign-in/sign-up →
workspace view (or "create your first workspace" panel).

Semantic contract (tests rely on these):

- `<h1>` "Workboard Lab"; header shows the signed-in email and a **"Sign out"**
  button.
- Sign-in form: `<label>`s **"Email"**, **"Password"**; button **"Sign in"**;
  failure → `role="alert"` message, no navigation. Toggle link-button
  **"Need an account? Create one"** / **"Already have an account? Sign in"**;
  sign-up adds **"Name"** and button **"Create account"**.
- Workspace selector: `<select>` labeled **"Workspace"** (options = workspace
  names, name ASC); role text **"Your role: Owner"/"Your role: Member"**;
  button **"New work item"** (`aria-expanded`).
- Item form labels: **"Title"** (input), **"Status"** (select with options
  `Open`, `In progress`, `Done`), **"Due date"** (`<input type="date">`),
  **"Notes"** (textarea). Buttons: **"Create work item"**, **"Save changes"**,
  **"Cancel"**. Per-field messages under fields, `aria-invalid` on error.
- Item list: `<ul>` with accessible name **"Work items"**; each item is a
  card (`li`) with an `<h3>` title, a status pill with the exact label text
  (`Open` / `In progress` / `Done`), a meta line `Updated <YYYY-MM-DD> ·`
  `Due <YYYY-MM-DD>` or `No due date`, and notes (verbatim, not trimmed).
- Row actions: **"Edit"** (aria-label `Edit <title>`), **"Delete"**
  (aria-label `Delete <title>`). Delete is a **two-step inline confirm**:
  first click turns the row's actions into **"Confirm delete"**
  (aria-label `Confirm delete <title>`) + **"Cancel"**; deletion happens only
  on confirm.
- First-run (no workspaces): panel "Create your first workspace" with label
  **"Workspace name"** and button **"Create workspace"**.
- Empty workspace: text "No work items in this workspace yet. Use "New work
  item" to add the first one."
- Feedback: a visually hidden `role="status"` live region announces
  "Work item created." / "Work item updated." / "Work item deleted." /
  "Workspace created."; errors appear as `role="alert"` banners.

**Documented baseline limitation (a task variant builds here):** when a
create/edit save fails, the form stays open with input preserved and shows
the API error; there is no draft persistence across reload, no retry
button on the mutation itself, and no version-conflict handling.

## 7. Repo layout & conventions

```
baseline/
  server/        Hono API (app.ts factory, api.ts routes, db.ts, auth.ts,
                 seed.ts, main.ts entry)
  scripts/       db-reset.ts
  shared/        pure domain logic + wire types (imported by server AND UI)
  src/           React SPA (components/, hooks/, api-client, auth-client)
  tests/unit     Vitest domain tests
  tests/api      Vitest integration tests (real Hono app + SQLite file)
  e2e/           Playwright specs + helpers
  docs/          this contract
```

Workspace-level documents (outside `baseline/`): `../contracts/` (draft task
contracts), `../docs/source-inventory.json`, `../docs/faq-draft.md`,
`../PREPARATION_PROVENANCE.md`.

- TypeScript strict; `verbatimModuleSyntax`; two tsconfigs (app: DOM, node:
  server/tests). No `any` in committed code.
- Server modules use ESM imports with `.js` suffixes (tsx/node ESM).
- Pure logic (validation, ordering, dates, ids) lives in `shared/` and must
  stay importable by both sides.
- ESLint flat config (`eslint.config.js`); `no-console` allowed in CLI/
  entrypoint files, warn elsewhere.
- Tests that claim persistence must open a **second SQLite connection** (or
  reload the page) rather than trusting in-memory state. Ownership tests
  must use two distinct real sessions.
- Do not weaken or delete baseline tests; add alongside them.

## 8. Explicit non-baseline (do NOT assume it exists)

Pagination/filters/search, archive/soft-delete/restore, import/export,
activity history, invites/membership management, bulk operations,
optimistic concurrency (client version hints), due-date semantics (relative
labels, overdue, calendar validation), draft persistence across reloads,
per-field trimming/length limits, deep links, dashboards/summaries, tags,
keyboard shortcuts, i18n, dark mode.

## 9. Uniqueness/scope guarantees for task authors

- One workspace per member set; no nesting. One DB per server process
  (env-selected path). No background jobs, no timers, no websockets.
- No rate limiting, no CSRF beyond Better Auth's origin checks
  (trusted origins include the Vite dev origin automatically).
- Server logs to stdout only. No file writes outside the DB path(s) under
  `data/` or `.tmp/`.
