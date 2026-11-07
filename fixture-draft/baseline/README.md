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
npm run check        # typecheck + lint + unit (11) + api (33)
npm run test:e2e     # 16 Playwright tests, real UI + API + SQLite (self-contained)
npm run check:full   # everything above
```

All commands exit 0 on success, nonzero on any failure.

## Where the truth lives

- **`docs/baseline-contract.md`** — schema, API, conventions, seed data,
  ownership/session rules, UI semantics. Normative.
- `docs/source-inventory.json` — official docs sources, versions, licenses.
- `../contracts/` — draft task contracts (DRAFT; not qualified).
