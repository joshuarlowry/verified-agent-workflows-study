# PREPARATION PROVENANCE — Workboard Lab fixture (Study 2)

Date: 2026-11-07 · Phase: preparation (fixture construction), NOT a scored
attempt. Endpoint reached per instructions: baseline + draft contracts
delivered; no reference implementations, no sealed tests, no calibration
runs.

## 1. Exact model / route

- Model: **z-ai/glm-5.3-flash** (agent identity string in the harness:
  `study2-glm-probe/glm`).
- Route: **OpenCode → LiteLLM → OpenRouter → Relace FP4**.
- No other models or subagents were invoked. All file edits, commands, and
  verifications in this workspace were produced by this single session.

## 2. Authorship disclosure (required)

The user authorized the three study models to construct and cross-review
fixtures in fresh separate sessions. Because those models are **not
independent model families**, the resulting review chain has no
independent-family authorship. The user waived family exclusion but **not**
disclosure or checks; this statement is the required disclosure. A separate
model will review this work in a fresh session; **this session cannot and
does not self-approve the fixture as independently qualified**, and nothing
in this workspace should be read as claiming independent qualification.

## 3. Artifacts

```
/workspace
├── PREPARATION_PROVENANCE.md          (this file)
├── README.md
├── docs/
│   ├── source-inventory.json          (official sources, versions, licenses, omissions)
│   └── faq-draft.md                   (DRAFT frozen product FAQ)
├── contracts/                         (19 DRAFT contracts + index)
│   ├── README.md
│   ├── C1-workspace-item-counts.md … C4-remember-last-workspace.md
│   └── S01-input-validation-hardening.md … S15-keyboard-quick-add-focus.md
└── baseline/                          (Workboard Lab application)
    ├── package.json / package-lock.json (exact pins, committed lockfile)
    ├── tsconfig.{json,app,node}.json — wait, see below
    ├── vite.config.ts / vitest.config.ts / playwright.config.ts / eslint.config.js
    ├── index.html
    ├── server/ (main, app, api, db, auth, seed, errors)
    ├── scripts/db-reset.ts
    ├── shared/ (domain.ts, types.ts)
    ├── src/ (React SPA: App, Workboard, ItemForm, AuthPanel, StatusPill, hooks)
    ├── tests/unit (3 files, 11 tests) / tests/api (4 files + helpers, 33 tests)
    ├── e2e (3 specs + helpers, 16 tests)
    └── docs/baseline-contract.md (canonical public baseline contract)
```

(Tsconfigs: `tsconfig.app.json` + `tsconfig.node.json`; there is no
`tsconfig.json` root file — `npm run typecheck` runs both configs
explicitly.)

## 4. Substantive decisions (with reasons)

1. **All 13 candidate pins kept, zero version changes.** Verified on the
   registry (`npm view pkg@version`), peer ranges checked (plugin-react→
   vite ^8; vitest 5→vite ^8; typescript-eslint 8.72.1→eslint ^10;
   react-hooks 7.1.1→eslint ^10; node-server→hono ^4), then exercised by
   real installs/builds/tests. Supporting picks: @types/node 24.19.2 (Node
   24 line), @types/react{,-dom} 19.3.0, @types/better-sqlite3 9.6.0
   (latest; documented type/runtime gap vs 13.0.3), @eslint/js 10.0.1,
   typescript-eslint 8.72.1, eslint-plugin-react-hooks 7.1.1, globals
   17.14.0.
2. **Better Auth 1.7.18 does not auto-create its tables.** First run threw
   `SchemaMismatchError (SCHEMA_MISMATCH)`. Chose the library's own
   programmatic migration (`better-auth/db/migration` →
   `getMigrations(auth.options).runMigrations()`), idempotent on every boot,
   instead of the CLI or hand-written DDL. Passing the `better-sqlite3`
   instance directly as `database` works (kysely stayed a transitive dep).
3. **Default API port 4310, not 8787.** The sandbox harness itself listens
   on 127.0.0.1:8787; picking a quiet default avoids EADDRINUSE for every
   downstream agent. e2e serves on 4599, dev UI on 5173 (proxy /api).
4. **Memberships owned by the app, not Better Auth's organization plugin**
   — keeps the baseline small and gives task variants a clean surface.
5. **Baseline mutation rule: any member can CRUD items; owner role exists
   but grants nothing** — documented as a gap so S06 (permissions) and S13
   (membership management) have real work.
6. **Version column present but last-write-wins** — S09 (optimistic
   concurrency) then adds the conditional-update path without touching
   schema.
7. **Deliberately imperfect baseline edges** (documented, each feeding
   exactly one task): no trimming/limits (→S01), no pagination (→S03), no
   export/import (→S04/S05), reload-loses-drafts (→S07), silent
   workspace-switch discard (→S10), raw date strings (→S08), hard delete
   only (→S02), no member management (→S13), no aggregates (→S14), no
   shortcuts (→S15), no bulk ops (→S11), no history (→S12), no deep links
   (→C3), no sort param (→C2), no counts (→C1), no selection restore (→C4).
8. **Seed design**: fixed IDs/timestamps for workspaces/items; users created
   through Better Auth (random ids, hashed passwords) with published
   public credentials; idempotent re-run; list order pinned by updated_at.
9. **Test strategy**: unit (pure domain), API tests through the real Hono
   app with real SQLite files (second-connection persistence proofs,
   cross-user ownership via real cookie sessions), Playwright e2e against
   the built SPA + API + seeded DB on one origin. Tests target semantic
   roles/labels (`getByRole`, `getByLabel`) — several strict-mode collisions
   found and fixed by making the product markup cleaner (removed a
   redundant `aria-labelledby` region label duplicating the select's name).
10. **Contracts are DRAFTs**: each has baseline-vs-task separation, exact
    public examples, non-goals, ownership, acceptance mapping, and advisory
    conflict notes. No reference implementation or sealed test was written
    for any task.

## 5. Diagnostics encountered and resolved

- Better Auth `SchemaMismatchError` on first use (see decision 2); transient
  "Database schema mismatch" ERROR logged by `runMigrations()` during
  first-time table creation even though creation succeeds; second boot is
  clean. Recorded in source-inventory.
- Server-side `auth.api.*` returns plain objects; HTTP path returns
  `{token,user}` — test helper initially parsed the wrong shape; fixed.
- `POST /api/auth/sign-out` with JSON content-type but empty body → 400;
  with `{}` → 200. UI client sends a proper body; API test covers it.
- Better Auth CSRF origin check rejects cookie POSTs whose `Origin` is not
  trusted (observed 403 from curl with untrusted Origin; requests without
  Origin, like in-process tests, pass). `WORKBOARD_TRUSTED_ORIGINS` +
  always-trusted Vite dev origins handle it.
- ESLint 10 flagged a real `no-useless-assignment` in `api-client.ts`; fixed.
- Two test-expectation bugs (alphabetical order of workspaces, comparator
  tiebreak direction) and one seed/assumption mismatch (ada has only
  Apollo; bruno is the dual-workspace member) — fixed in tests/contracts,
  product unchanged.
- Playwright `getByLabel`/`getByRole` substring matching caused strict-mode
  violations ("Notes" vs "Edit Write release notes"); fixed with
  `exact: true` in tests, plus the markup fix in decision 9.
- `pkill -f tsx` killed my own shell (pattern matched the wrapper command);
  switched to port-targeted `fuser -k`.

## 6. Verification record (final state)

All from `baseline/`, Node v24.19.0, npm 10.9.0:

| Check | Command | Result | Exit |
|---|---|---|---|
| Typecheck | `npm run typecheck` (both tsconfigs) | clean | 0 |
| Lint | `npm run lint` (eslint 10.14.0, flat config) | clean | 0 |
| Build | `npm run build` (vite 8.3.6) | 68 modules, dist ~264 kB js | 0 |
| Unit/domain | `npm run test:unit` | 11/11 passed (3 files) | 0 |
| API/DB | `npm run test:api` | 33/33 passed (4 files) | 0 |
| E2E | `npm run test:e2e` | 16/16 passed (~12 s) | 0 |
| Full | `npm run check:full` | all of the above | 0 |
| Live smoke | server + seeded db + curl CRUD cycle | signin 200, create 201, patch version→2, delete 204, signout 200, /api/me 401 after | ok |
| Lockfile | `package-lock.json` | present; 21 tracked packages consistent lockfile↔node_modules | ok |

## 7. Unresolved issues / what remains unqualified

1. **Everything in `contracts/` is DRAFT and unqualified.** No task has a
   reference implementation or sealed test; solvability, example accuracy
   under implementation, and acceptance completeness are unproven. The C1
   and S14 count examples were self-corrected during drafting (Apollo open
   = 4) — reviewers should re-verify every numeric example against the
   seed.
2. **No Context archives exist** for the packages; `docs/source-inventory.json`
   lists official sources and live-verified behaviors only, and explicitly
   does not claim archive construction or review.
3. **Same-family review caveat**: reviewers are same-family models; treat
   their confirmations as same-family evidence, not independent replication.
4. Known cosmetic debt (intentional baseline): timestamps rendered as raw
   date substrings; two-step delete is plain buttons (no dialog); no visual
   assets. All within "polished but modest" scope.
5. FAQ/provenance truthfulness notes: Better Auth internals beyond the
   verified paths remain undocumented (recorded in source-inventory); the
   sandbox's 8787 listener is external to this fixture and documented as a
   port constraint.
6. Per instructions, this session stopped at the preparation endpoint: no
   study models were run on the task contracts and no calibration was
   started.
