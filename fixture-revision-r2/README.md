# Verified Agent Workflows — Study 2 fixture (preparation output, revision R2)

Workspace contents:

- **`baseline/`** — Workboard Lab: the frozen baseline application
  (React 19 + Hono + SQLite + Better Auth). Read
  `baseline/docs/baseline-contract.md` first; it is normative.
- **`contracts/`** — 19 DRAFT task contracts (4 calibration, 15 scored).
  Drafted, then revised in repair sessions R1 and R2; **not qualified**; no
  reference implementations or sealed tests exist yet.
- **`docs/`** — `source-inventory.json` (official sources, retrieval
  context, documented omissions) and `faq-draft.md` (draft frozen product
  FAQ, including questions that cannot be settled honestly).
- **`PREPARATION_PROVENANCE.md`** — the first builder endpoint's provenance
  (historical record; unchanged).
- **`REPAIR_PROVENANCE_R1.md`** / **`REPAIR_DISPOSITIONS_R1.json`** — the R1
  repair session's record: prior source identity, per-finding dispositions,
  commands/exit codes, remaining limitations (kept unchanged as history).
- **`REPAIR_PROVENANCE_R2.md`** / **`REPAIR_DISPOSITIONS_R2.json`** — the R2
  repair session's record (this revision), same structure as R1.
- **`r2-endpoint-manifest.json`** — the R2 endpoint's 73-file source
  manifest (per-file SHA-256 + sizes + tree hash), exported for the next
  review session.
- **`review-inputs/`** — immutable inputs for the R2 repair session
  (Terra's R1 cross-review + the verified R1-endpoint manifest). They are
  session inputs, not fixture source: they sit outside the source manifests
  and are never edited (the directory is mounted read-only).

Verification: `cd baseline && npm run check:full` → exit 0 (typecheck, lint,
build, 11 unit, 36 API/database, 20 Playwright e2e tests). Before the first
e2e run, install the pinned Playwright chromium headless shell once (see
`baseline/README.md`; if you relocate the browser cache, the
`PLAYWRIGHT_BROWSERS_PATH` variable must be set for both the install and
every run).

Preparation endpoint reached: no calibration runs, no study models executed
against the contracts; reference/sealed-test phases not started. A fresh
different-model review of revision R2 is still required (the R2 session did
not review or approve its own revision).
