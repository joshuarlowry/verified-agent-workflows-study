# Verified Agent Workflows — Study 2 fixture (preparation repair R3)

Workspace contents:

- **`baseline/`** — Workboard Lab (React 19 + Hono + SQLite + Better Auth).
  Read `baseline/docs/baseline-contract.md`; the R3 baseline is a construction
  candidate, not yet re-reviewed or qualified.
- **`contracts/`** — 19 draft task contracts (4 calibration, 15 scored),
  not qualified; no reference implementations or sealed tests exist here.
- **`docs/`** — official source inventory and draft FAQ.
- **`PREPARATION_PROVENANCE.md`**, **`REPAIR_PROVENANCE_R1.md`** /
  **`REPAIR_DISPOSITIONS_R1.json`**, **`REPAIR_PROVENANCE_R2.md`** /
  **`REPAIR_DISPOSITIONS_R2.json`** — unchanged historical records.
- **`REPAIR_PROVENANCE_R3.md`** / **`REPAIR_DISPOSITIONS_R3.json`** — this
  construction revision, evidence, commands and limitations.
- **`r2-endpoint-manifest.json`** — historical R2 inner manifest, not the
  current tree identity. `r3-endpoint-manifest.json` identifies R3 sources.
- **`review-inputs/`** — the delivered immutable R2 review at
  `review-inputs/terra-r2-review.json`, its verified outer manifest at
  `review-inputs/prior-endpoint-manifest.json`, and retained review
  diagnostics. This is not the historical R2 session's R1 review mount;
  that R1 review and its original endpoint manifest are not supplied here.
  Historical records describe their then-current paths, not today's mount.
- **`outputs/r3/`** — retained construction diagnostics and check logs,
  outside the application source.

Run `npm run check:full` in `baseline/`. Before e2e, install the pinned
Playwright chromium headless shell (see `baseline/README.md`); if relocating
its cache, use the same `PLAYWRIGHT_BROWSERS_PATH` for install and run. See
R3 provenance for actual verification and the OS fallback warning.

This is preparation construction, not a scored rescue, calibration or
qualification. GLM authored the preserved baseline and prior repairs; Terra
owns R3. Subject-model authorship/review is not independent-family evidence.
A fresh GLM cross-review is required after this endpoint; self-review is not
cross-review approval.
