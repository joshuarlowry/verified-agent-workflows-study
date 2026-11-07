# REPAIR PROVENANCE — Revision R1 (Workboard Lab fixture, Study 2)

Date: 2026-11-07 · Phase: preparation repair (revision R1) against the
different-model review in `review-inputs/terra-fixture-review.json`. This is
**not** a scored-run rescue, not qualification, and not a task attempt.
Endpoint reached per instructions: revised baseline + contracts + FAQ +
inventory delivered, with disposition and provenance records; the session
**stopped before any self-review or approval step**.

Companion machine record: `REPAIR_DISPOSITIONS_R1.json` (per-finding
dispositions, evidence, remaining limitations). This file is the human
provenance record; the two agree.

## 1. Exact model / route

- Model: **z-ai/glm-5.3-flash** (harness identity string:
  `study2-glm-probe/glm`).
- Route: **OpenCode → LiteLLM → OpenRouter → Relace FP4**.
- No other models or subagents were invoked. All edits, commands, and
  verifications in this repair were produced by this single session.

## 2. Prior source identity (what this session received and verified)

The workspace copy at session start was verified bit-identical to the
first builder endpoint before any edit:

- Manifest: `review-inputs/first-endpoint-manifest.json` — 68 files,
  declared tree `sha256:1f0b63fae9392282474183f4015bf3599c5a32c6d9bbc1c39d65a9e895e72ad3`.
- **All 68 source paths and per-file SHA-256 values matched** this
  workspace copy (checked one by one, before any edit).
- The review report's independent tree hash (its own algorithm, run on its
  own copy) was recomputed here and matched:
  `cd25e6e35a5f2a81952e1bdf0a53ce4c5c6dbc0467f84eb830011cbab4eee142`
  (`…142`). So builder, reviewer, and this repair session all started from
  the same identified source state.
- The review report `review-inputs/terra-fixture-review.json` was read in
  full (all 13 assigned findings) and treated as **immutable** — it was
  never edited.
- `PREPARATION_PROVENANCE.md` (the first endpoint's record) was left
  unchanged on purpose, including its now-outdated test counts
  (unit 11 / api 33 / e2e 16); it is the historical record of the first
  session, not of this one.

## 3. Authorship disclosure (required, same statement as R1 dispositions)

This repair was authored by the **same subject-model family (GLM)** as the
original fixture builder. The review it implements was authored by a
different study model (Terra) — but the study models are also **not
independent model families**. Cross-review within the authorized study
models is disclosed as **same-family evidence, not independent
replication**. The user waived family exclusion but not disclosure. This
session did **not** cross-review or approve its own revision; it stopped
before that step. Nothing here claims independent qualification.

## 4. Scope respected

- **Implemented (13 findings):** B1, B2, B3, C1, C2, S1, S2, S3, S4, S5,
  S6, A1, D1 — each dispositioned in `REPAIR_DISPOSITIONS_R1.json`.
- **Not touched:** U1–U3 (coordinator usage schema/normalizer) — outside
  this application workspace; handled separately with recorded review.
- **Deliberately not done (by design):**
  - No reference solutions, sealed tests, or oracles created or claimed.
  - No task features implemented into the baseline — deliberately missing
    task features stay missing.
  - No calibration or scoring runs; no three-clean-instance or
    qualification work; none claimed.
  - No new npm dependencies; lockfile pins unchanged (`npm ci` from the
    committed lockfile only).
  - No databases beyond new local disposable SQLite files
    (`baseline/.tmp/e2e.db*`, `:memory:` probes); no deploys, no pushes.
  - The intentionally unguarded edit-discard behavior (S10's increment)
    was **preserved**; B1 fixed only the unintended stale-data bug.

## 5. Per-finding disposition summary (essence)

| Finding | Disposition | Essence |
|---|---|---|
| B1 | fixed_in_baseline | `useJson` keyed by request path; cross-path switch clears data/error immediately (derived view, no stale paint); same-path refetch failures keep old data; new e2e `switch.spec.ts` (delayed + failed switch). |
| B2 | docs_reconciled_implementation_kept | Route resolution precedes auth: unknown endpoints/unsupported methods → 404 app envelope; Better Auth routes use native `{message, code}` body (verified by probe); wrong-password api test extended. |
| B3 | documented_and_isolation_hardened | `reuseExistingServer: false` in playwright config; browser install documented as one-time prerequisite and installed in this session's private cache. |
| C1 | examples_corrected_and_migration_scope_enumerated | Counts corrected 5/3 → 4/3; exhaustive enumerated test migrations (auth.spec option texts, ownership.spec selectOption labels); uniform test-migration precedence rule published (contracts/README + FAQ Q11). |
| C2 | examples_corrected | `title_asc` first = "Archive old assets"; exact id sequences published for all three sorts. |
| S1 | contracts_reconciled_with_enumerated_migrations | Unified title message "title must be 1-120 characters."; enumerated migrations; S08 helper takes day strings, UTC-flip documented, time-robust testing policy. |
| S2 | wording_fixed_consistency_model_published | Archived excluded from default/active, `filter=archived` archived-only, unknown filter → 400; S03 realizable no-repeats-within-walk model under monotonic `updated_at`, no snapshot promises. |
| S3 | export_contract_corrected | Correct `created_at` ASC order; `workspaceId` added to exact shape; equality defined after camelCase mapping. |
| S4 | permission_and_payload_policies_defined | Rename rule = actual change only; `error.fields` stays string-valued, typed `error.currentItem` as the single documented exception; `GET /api/items/:id` added as refetch path. |
| S5 | examples_and_rules_corrected | `bruno` for dual-workspace examples; dirty = differs-from-pristine + exact form titles; consistent S11 numbers, duplicates → 400, foreign ids anti-leak; S04 array-level 400 messages + lowest-index-wins 422 priority. |
| S6 | boundaries_and_grammars_defined | S07 auto-restore with "Draft restored." banner as disclosure, dirty-trigger defined; S08 label grammar; S12 field set/atomicity/limits; S15 baseline described as keyboard-operable with no shortcuts. |
| A1 | policy_settled_and_published | Reset-to-baseline per task settled (contracts/README + FAQ Q18); overlap advisories expanded; no combined-task acceptance assumptions. |
| D1 | inventory_expanded_and_paths_fixed | `system_sources` added (Node 24, SQLite, MDN, WAI-ARIA APG) with retrieval dates/version context/coverage+omission statements; license fields null with not-verified note; baseline README inventory path fixed. |

Full policy choices, change lists, evidence, and remaining limitations per
finding are in `REPAIR_DISPOSITIONS_R1.json`.

## 6. Substantive edits (actual files changed)

Verified by mtime scan; consistent with the dispositions' change lists.
Nothing outside this list was modified (S13/S14 contracts untouched; the
review inputs untouched).

**Baseline code / tests / config:**
- `baseline/src/hooks/useJson.ts` — rewritten (B1).
- `baseline/e2e/switch.spec.ts` — **new** public regression spec (B1).
- `baseline/tests/api/auth.test.ts` — wrong-password body pinned; new
  unsupported-method 404 test (B2).
- `baseline/playwright.config.ts` — `reuseExistingServer: false` (B3).

**Baseline docs:**
- `baseline/docs/baseline-contract.md` — §2 browser/isolation, §5 error
  precedence, §6 switch freshness + intentional-discard note (B1/B2/B3).
- `baseline/README.md` — prerequisites + corrected inventory path (B3/D1).

**Contracts (17 files + index):**
- `contracts/README.md` — authorship rewording, reset policy (settled at
  R1), uniform baseline-test-edit precedence rule, expanded advisories.
- C1, C2, C3, C4, S01–S12, S15 — each revised per its finding(s).
- S13, S14 — **unchanged** (no findings against them).

**Docs:**
- `docs/faq-draft.md` — rewritten Q1–Q18; open questions trimmed to 4.
- `docs/source-inventory.json` — rewritten with `system_sources`,
  verification, coverage/omission statements (JSON-validated).

**Root:**
- `README.md` — revision-R1 framing, updated test counts (11 / 34 / 18).

**New records / diagnostics:**
- `REPAIR_DISPOSITIONS_R1.json`, `REPAIR_PROVENANCE_R1.md` (this file).
- `diagnostics/error-format-probe.mts` — B2 evidence probe (outside
  `baseline/`, non-authoritative diagnostic).

**Generated, disposable, not source:** `baseline/dist/*` (build output),
`baseline/.tmp/e2e.db{,-shm,-wal}` (disposable seeded SQLite from e2e runs),
`baseline/test-results/.last-run.json` (Playwright artifact).

## 7. Verification record (exact commands and exit codes)

All from `baseline/` unless noted; Node v24.19.0, npm 10.9.0.

| # | Command | Result | Exit |
|---|---|---|---|
| 1 | `npm ci --no-audit --no-fund` | fresh install from committed lockfile; pins unchanged | 0 |
| 2 | `npm run typecheck` | clean | 0 |
| 3 | `npm run lint` | clean | 0 |
| 4 | `npm run test:unit` | 11/11 (unchanged count) | 0 |
| 5 | `npm run test:api` | 34/34 (33 existing + 1 new route-precedence test) | 0 |
| 6 | `CI=1 PLAYWRIGHT_BROWSERS_PATH=/workspace/.cache/ms-playwright npm run test:e2e` | 18/18 (16 existing + 2 new switch regressions) | 0 |
| 7 | `npm run build` | clean | 0 |
| 8 | `CI=1 PLAYWRIGHT_BROWSERS_PATH=/workspace/.cache/ms-playwright npm run check:full` | all of the above, final clean run | 0 |
| 9 | `PLAYWRIGHT_BROWSERS_PATH=/workspace/.cache/ms-playwright npx playwright install chromium --only-shell` | chromium_headless_shell-1254 + ffmpeg-1013 into this session's private cache | 0 |
| 10 | `python3 -m json.tool docs/source-inventory.json` | parses | 0 |
| 11 | tree-identity recomputation vs manifest (python) | 68/68 files matched pre-edit; tree hash `cd25e6e3…142` matches review | 0 |

Ordering check: the last baseline source edit was at 04:14 UTC; the final
`check:full` (which rebuilt `dist/`) ran at 04:23 UTC. **No baseline file
changed after the final verification run.** The only file written since is
this record and the (already-validated) dispositions JSON, both outside
`baseline/`.

## 8. Diagnostics encountered and resolved

- **B2 evidence probe** (`diagnostics/error-format-probe.mts`, run with
  tsx): unknown endpoint → 404 app envelope
  `{"error":{"code":"not_found",…}}`; wrong credentials on a Better Auth
  route → 401 `{"message":"Invalid email or password","code":"INVALID_EMAIL_OR_PASSWORD"}`
  (native format, no app envelope); `DELETE /api/health` → 404 envelope.
  These observed outputs drove the §5 contract reconciliation.
- **E2E empty-list visibility quirk:** an empty `<ul>` is treated as
  hidden by Playwright; presence assertions during gated/empty states use
  `toHaveCount(1)` rather than `toBeVisible()`. Encountered while writing
  the delayed-switch regression; resolved in the spec.
- **Deterministic delayed-switch test:** implemented with route gating
  (`route.fetch()` held on a promise gate, then `fulfill`) so the
  stale-paint window is reproducible; the failed-switch test uses
  `route.abort()` plus unroute + Retry for the recovery path.

## 9. Unresolved questions (carried forward)

1. The revised (R1) contracts have **not been re-reviewed** by any second
   session; self-review was explicitly not performed (stop point).
2. Better Auth internals beyond the verified error paths remain
   undocumented (FAQ open question).
3. Scoring weights, final corpus packaging, and qualification remain
   coordinator-owned; the reset-per-task policy here is a preparation-phase
   default, not a qualification decision.
4. Playwright's OS-fallback warning behavior may differ on other platforms.
5. S01's enumerated test migrations (and every other contract-side
   acceptance detail) can only be verified when their tasks are
   implemented; equivalence is enforced by contract text and implementer
   recording.

## 10. What remains unqualified / explicitly not done

- All 19 contracts remain **DRAFT and unqualified**: no reference
  implementations, no sealed tests, no oracles exist; task solvability and
  acceptance completeness are unproven.
- No Context archives were built; `docs/source-inventory.json` documents
  official sources with retrieval context and explicit omissions, and
  license fields for documentation sources are null with a not-verified
  note (no invented upstream facts).
- U1–U3 were not touched and are not dispositioned here.
- Per instructions, this session **stopped at the repair endpoint**: no
  self-review, no cross-review of the revision, no approval, no calibration,
  no qualification claims.
