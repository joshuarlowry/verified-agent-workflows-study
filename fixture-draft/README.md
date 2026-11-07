# Verified Agent Workflows — Study 2 fixture (preparation output)

Workspace contents:

- **`baseline/`** — Workboard Lab: the frozen baseline application
  (React 19 + Hono + SQLite + Better Auth). Read
  `baseline/docs/baseline-contract.md` first; it is normative.
- **`contracts/`** — 19 DRAFT task contracts (4 calibration, 15 scored).
  Drafted only; **not qualified**; no reference implementations or sealed
  tests exist yet.
- **`docs/`** — `source-inventory.json` (official sources, verified
  versions/licenses, documented omissions) and `faq-draft.md` (draft frozen
  product FAQ, including questions that cannot be settled honestly).
- **`PREPARATION_PROVENANCE.md`** — exact model/route, decisions,
  diagnostics, verification record, and the required authorship-disclosure
  statement (no independent-family authorship; reviewer disclosure applies).

Verification: `cd baseline && npm run check:full` → exit 0 (typecheck, lint,
build, 11 unit, 33 API/database, 16 Playwright e2e tests).

Preparation endpoint reached: no calibration runs, no study models executed
against the contracts.
