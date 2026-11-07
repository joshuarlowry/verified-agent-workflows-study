# Verified Agent Workflows — Study 2 fixture (preparation output, revision R1)

Workspace contents:

- **`baseline/`** — Workboard Lab: the frozen baseline application
  (React 19 + Hono + SQLite + Better Auth). Read
  `baseline/docs/baseline-contract.md` first; it is normative.
- **`contracts/`** — 19 DRAFT task contracts (4 calibration, 15 scored).
  Drafted, then revised in repair session R1; **not qualified**; no
  reference implementations or sealed tests exist yet.
- **`docs/`** — `source-inventory.json` (official sources, retrieval
  context, documented omissions) and `faq-draft.md` (draft frozen product
  FAQ, including questions that cannot be settled honestly).
- **`PREPARATION_PROVENANCE.md`** — the first builder endpoint's provenance
  (historical record; unchanged).
- **`REPAIR_PROVENANCE_R1.md`** / **`REPAIR_DISPOSITIONS_R1.json`** — the R1
  repair session's record: prior source identity, per-finding dispositions,
  commands/exit codes, remaining limitations.
- **`review-inputs/`** — immutable inputs for this repair session
  (different-model cross-review + manifest).

Verification: `cd baseline && npm run check:full` → exit 0 (typecheck, lint,
build, 11 unit, 34 API/database, 18 Playwright e2e tests). Before the first
e2e run, install the pinned Playwright chromium headless shell once (see
`baseline/README.md`).

Preparation endpoint reached: no calibration runs, no study models executed
against the contracts; reference/sealed-test phases not started.
