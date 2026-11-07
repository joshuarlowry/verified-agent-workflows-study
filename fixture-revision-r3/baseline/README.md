# Workboard Lab

A small local work-item tracker: React 19 SPA + Hono API + SQLite
(better-sqlite3) + Better Auth email/password sessions. Built as the
**baseline fixture** for Verified Agent Workflows Study 2 — task variants
extend exactly what `docs/baseline-contract.md` says, nothing more.

## Quickstart

```bash
npm install          # Node 24.19.0 required
npm run db:reset     # recreate + seed data/workboard.db (see credentials below)
npm run dev:api      # Hono API on http://localhost:4310
npm run dev          # UI on http://localhost:5173 (proxies /api)
```

Seeded demo accounts (public test data):

| Email | Password |
|---|---|
| `ada@workboard.test` | `ada-passphrase-01` |
| `bruno@workboard.test` | `bruno-passphrase-02` |
| `cleo@workboard.test` | `cleo-passphrase-03` |

## Verification

```bash
npm run check        # typecheck + lint + unit (11) + api (36)
npm run test:e2e     # 20 Playwright tests, real UI + API + SQLite (self-contained)
npm run check:full   # everything above
```

All commands exit 0 on success, nonzero on any failure.

### Browser prerequisite for e2e

`@playwright/test` 1.65.0 does not download browsers during `npm ci`.
Before the first `test:e2e` / `check:full` run, install the pinned chromium
headless shell once. Two working setups:

```bash
# (a) default cache — fine when HOME is writable and stable between
#     the install and the test run:
npx playwright install chromium --only-shell
npm run test:e2e

# (b) relocated cache — the SAME variable must be set for BOTH the install
#     and every run (export it, or prefix each command):
export PLAYWRIGHT_BROWSERS_PATH=/workspace/.cache/ms-playwright
npx playwright install chromium --only-shell
npm run test:e2e
```

If the variable is set for the install but missing for the run, Playwright
looks in the default cache, finds no browser, and exits 1 ("Executable
doesn't exist") — that mismatch, not the install itself, is the common
failure. The e2e project runs headless chromium, so the headless shell is
enough; no other browser is required.

OS prerequisites: the headless shell needs chromium's shared libraries
(NSS, fontconfig, and related system packages). If a launch fails with
missing libraries, run `npx playwright install-deps chromium` (or install
the distribution's chromium dependencies). On the preparation sandbox the
host OS could not be read (`/etc/os-release` unavailable); Playwright's
banner reported an unsupported host and used its Ubuntu 24.04 fallback
build, after which the tests passed — treat "Ubuntu 24.04" as the
fallback's label, not a verified host OS.

The e2e webServer never reuses an already-running
server (`reuseExistingServer: false`): each run owns its freshly reset
`.tmp/e2e.db` on 127.0.0.1:4599, and a foreign listener on that port fails
the run loudly instead of being silently reused.

## Where the truth lives

- **`docs/baseline-contract.md`** — schema, API, conventions, seed data,
  ownership/session rules, UI semantics. Normative.
- `../docs/source-inventory.json` — official docs sources, versions,
  retrieval context, documented omissions (workspace-level, outside
  `baseline/`).
- `../contracts/` — draft task contracts (DRAFT; not qualified).
