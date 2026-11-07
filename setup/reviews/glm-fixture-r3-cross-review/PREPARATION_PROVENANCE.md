# PREPARATION PROVENANCE — Fresh GLM cross-review of the R3 fixture endpoint

Phase: fresh cross-review endpoint. This session did not construct, repair,
score, calibrate, or qualify anything; it reviewed Terra's R3 preparation-repair
endpoint and wrote `FIXTURE_R3_CROSS_REVIEW.json` (companion to this file).
Identity/timing below are harness-reported; the controller's records are
authoritative and supplement anything not independently resolvable here.

## 1. Identity and scope (disclosed)

- Requested model/route: **GLM (z-ai/glm-5.3-flash)** via
  OpenCode → LiteLLM → OpenRouter → Relace FP4; harness identity
  `study2-glm-probe/glm`. The exact upstream revision and route were **not**
  independently resolved from the harness alias; controller evidence is
  authoritative for session identity, routing and timing.
- No other models or subagents were invoked. All commands, inspections and
  files in this review were produced by this single session.
- **Subject-model disclosure:** GLM authored the preserved baseline and the
  R1/R2 repairs; Terra authored R3; this session is a fresh GLM cross-review
  of Terra's R3. Gemma, GLM and Terra are the only authorized model families
  and are the benchmark's subjects, so this review is disclosed subject-model
  cross-review, **not** independent-family evidence. Findings stand or fall
  on the reproduced substance, not on reviewer identity.
- This review **does not approve** references, sealed controls, calibration or
  qualification; a consistency verdict does not qualify nonexistent
  references or sealed controls.

## 2. What was reviewed

Delivered immutable inputs under `/workspace/inputs/`:

- `endpoint-manifest.json` — R3 outer manifest (78 entries; also covers the
  inner manifest itself).
- `fixture/r3-endpoint-manifest.json` — R3 inner manifest (77 entries).
- `fixture/r2-endpoint-manifest.json` — historical R2 inner manifest
  (73 entries; unchanged historical record).
- `prior-review.json` — the immutable R2 review (external to the fixture tree).
- `fixture/` — baseline app, 19 draft contracts, docs, provenance/disposition
  records R1–R3.

The R2→R3 changeset computed from the manifests is exactly 12 modified +
4 new files, matching Terra's declared repair surface; every other file is
byte-identical to its R2 manifest entry.

## 3. Verification performed (all retained under /workspace/diagnostics)

| Check | Result |
|---|---|
| Manifest identity: 77 inner + 78 outer entries — every path a regular file, sizes and SHA-256 match; no extra/missing files; tree hashes match claims; outer covers the inner manifest byte-exactly; independent path/NUL/hash/LF digests recorded | exit 0 (`source-hashes-final.txt`); re-run after diagnostics with `cmp` clean → inputs byte-identical throughout |
| Fresh scratch install (`scratch-r3`): `npm ci`, Playwright chromium headless shell, `CI=1 … npm run check:full` | exit 0: typecheck + lint clean, **11 unit, 36 API, 41 e2e** (7 auth + 21 isolation + 6 items + 3 ownership + 4 switch) — matches Terra's claimed final counts |
| S03 keyset model: independent simulation of the contract's exact strict predicate over the real seeded DB (15 checks: page sequences, future-key admits, conditional guarantees, stronger sufficient condition, 20/21 threshold, nextCursor-null semantics) | exit 0, 15/15 PASS (`keyset-r3.log`) |
| HTTP surface: 21 documented claims reproduced against the real app (HEAD health/me/get-session/unknown, envelopes with/without session, Better Auth native responses, wrong-password shape) | exit 0, 21/21 PASS (`routes-r3.log`) |
| Seed facts for C1 (Apollo 8 items / 4 open; Borealis 5 / 3 open) and C2's three seed orderings (SQL over the seeded DB) | all match the contracts |
| C1 migration census (grep over all e2e specs) | matches C1's enumerated scope exactly; status selectors excluded and untouched; auth.spec option-text assertions match one-for-one |
| Mutant check on the SCRATCH copy only (guards disabled: `isCurrent → () => true`): isolation held-success tests | 5/5 FAIL on concrete assertions after the processing barrier (not timeouts) → the new guards/barriers are load-bearing; scratch restored afterwards and diff-clean against the input; isolation re-run green (21/21) |
| Static review of the R3 changeset (Workboard.tsx, ItemForm.tsx, helpers.ts, switch/isolation/auth specs, auth.test.ts, baseline-contract, C1, contracts/README, S03, S10, README, FAQ) | control-flow walk of every mutation completion/caller; every R2 defect path closed; per-contract traces recorded in the JSON |

Diagnostic scripts are retained (`diagnostic-r3-keyset.mts`,
`diagnostic-r3-routes.mts`, `verify_r3_sources.py`) alongside all logs.
The mutation was applied **only** to the scratch copy and reverted; the
immutable inputs were never modified.

## 4. Verdict summary

- **Baseline:** consistent; freeze-ready candidate for the next phase (R2-N1
  and R2-N2 repaired and independently verified). Not qualified.
- **C1–C4:** all four CAN PROCEED to reference/alternate/evaluator
  construction on draft terms (C1's migration scope corrected and verified;
  C2/C3/C4 carried over consistent). None qualified; nothing solvability-proven.
- **S03, S10:** consistent drafts; CAN PROCEED (model and compatibility choice
  verified on paper and by reproduction). Unimplemented, unqualified.
- **S01, S02, S04–S09, S11–S15:** byte-identical to R2; R2 verdicts and
  qualification limitations carry over; no new defects found in scope.
- **New low-severity documentation defects:** R3-N1 (FAQ self-labels as
  "revision R1" while containing R2/R3 content) and R3-N2 (README/dispositions
  reference construction-time `review-inputs/` and `outputs/r3/` paths absent
  from the delivered source-only export — the honest partial residual of
  R2-N6). Neither is behavioral, neither blocks construction.

## 5. Limits

- The R2 outer manifest and Terra's `outputs/r3/` diagnostic logs are not part
  of this delivery; Terra's pre-edit verification, initial-red and mutant logs
  remain historical claims. This session re-verified the substantive behaviors
  independently instead.
- `prior-review.json`'s self-recorded hash is self-referential (cannot match a
  file that contains it); its integrity is a controller-anchor matter.
- The R1 source tree/manifest were never supplied in any revision; R1-era
  repair claims remain historical and were not reconstructed.
- The response-processing barrier is implementation-aware (consumption marker
  + timer + two frames), not a formal event-loop proof; unusual scheduling,
  network failure shapes and multi-click overlaps remain qualification scope.
- No S03/S10/C1 implementation, reference, alternate, sealed evaluator,
  controlled-clock acceptance test or calibration exists; none was built here.
- Anything outside the supplied files (including U1–U3, provider usage,
  billing, session ancestry) has no disposition here.

## 6. Stop point

Stopped at the honest fresh-review endpoint: immutable inputs verified
unchanged before and after all diagnostics; no fixes implemented, no task
solutions, no test weakening, no calibration started, no scored runs, no
worker/model calls, no account/budget/production changes, no deploy, push or
merge. Self-authored diagnostics under `/workspace/diagnostics` are review
evidence, not acceptance fixtures.
