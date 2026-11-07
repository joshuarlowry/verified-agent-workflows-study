# REPAIR PROVENANCE — Revision R2 (Workboard Lab fixture, Study 2)

Date: 2026-11-07 · Phase: preparation repair (revision R2) against the
different-study-model review in `review-inputs/terra-r1-cross-review.json`
(Terra's R1 cross-review of the R1 endpoint). This is **not** a scored-run
rescue, not qualification, and not a task attempt. Endpoint reached per
instructions: revised baseline + contracts + FAQ + inventory delivered, with
disposition and provenance records; the session **stopped before any
self-review or approval step**.

Companion machine record: `REPAIR_DISPOSITIONS_R2.json` (per-finding
dispositions, evidence, remaining limitations). This file is the human
provenance record; the two agree.

## 1. Exact model / route

- Model: **z-ai/glm-5.3-flash** (harness identity string:
  `study2-glm-probe/glm`).
- Route: **OpenCode → LiteLLM → OpenRouter → Relace FP4**.
- No other models or subagents were invoked. All edits, commands, and
  verifications in this repair were produced by this single session.

## 2. Prior source identity (what this session received and verified)

The workspace copy at session start was verified bit-identical to the R1
endpoint before any edit:

- Manifest: `review-inputs/prior-endpoint-manifest.json` — 71 files,
  declared tree
  `sha256:35f22c5abce72cdc9956d428ab40ceefe9d42e285402ef34c686f1a016eb4b6b`
  (`…eb4b`).
- **All 71 source paths and per-file SHA-256 values matched** this
  workspace copy (checked one by one, before any edit).
- The review's independent tree hash (Terra's own algorithm — per-path
  records of UTF-8 path + NUL + lowercase SHA-256 + LF, byte-wise sorted,
  over the same 71 files) was recomputed here and matched byte-for-byte:
  `00143dd91ccf0aec27c202e8058c74575aa97fcb5483eae8eef7e7112b58d6c4`
  (`…d6c4`). The manifest's own canonical array hash was also reproduced
  from its recorded per-file values (byte-wise sorted keys `bytes`,
  `path`, `sha256`, compact separators, entries in manifest order). So R1,
  Terra, and this repair session all started from the same identified
  source state.
- The review report `review-inputs/terra-r1-cross-review.json` was read in
  full (all 9 new defects R1-N1…R1-N9, plus its verification and limits)
  and treated as **immutable** — it was never edited.
- `REPAIR_PROVENANCE_R1.md` and `REPAIR_DISPOSITIONS_R1.json` were left
  unchanged on purpose as the historical record (their hashes re-verified
  unchanged at the R2 endpoint); including R1's now-outdated counts
  (unit 11 / api 34 / e2e 18) inside them.

## 3. Authorship disclosure (required, same statement as R2 dispositions)

This repair was authored by the **same subject-model family (GLM)** as the
original fixture builder and the R1 repair session (all
z-ai/glm-5.3-flash). The review it implements was authored by a different
study model (Terra), which is also not an independent family. Cross-review
within the authorized study models is disclosed as **same-family evidence,
not independent replication**. This session did **not** cross-review or
approve its own revision: a fresh **different-model review of revision R2
is still required** before any qualification step.

## 4. Scope respected

Implemented exactly the nine assigned new defects, nothing else:

- **R1-N1** (high) — delayed action completion must stay scoped to its own
  workspace (headline item: the defect Terra reproduced where a late
  Apollo create/delete response closed the Borealis form, dropped unsaved
  input, or announced into Borealis's live region).
- **R1-N2** (medium) — HTTP route/method precedence documented at observed
  granularity; representative exception tests added.
- **R1-N3** (high) — C1's permitted-migration list now authorizes the exact
  assertion-only switch.spec.ts selector migrations.
- **R1-N4** (high) — S08 enumerates its exact permitted public assertion
  migrations (items.spec.ts string; one playwright.config.ts env line).
- **R1-N5** (high) — S08 defines the server→client time interface (envelope
  `today`, per-item `dueState`) and a pinned deterministic test clock.
- **R1-N6** (high) — S03 rewritten to an attainable tie/concurrency model;
  the >=20 acceptance off-by-one fixed.
- **R1-N7** (medium) — S04 import diagnostics reconciled (missing vs empty
  title; non-object entries; precedence).
- **R1-N8** (medium) — S07 draft trigger fixed to "changed while the form
  is open" with explicit pristine-reversion semantics.
- **R1-N9** (medium) — browser install/run cache consistency, accurate OS
  support labeling, and document paths corrected.

Not done by design: no reference solutions or sealed tests; no task
features implemented into the baseline; the intentionally unguarded
switch-time draft discard (S10's increment) preserved; no calibration or
scoring runs; no new dependencies (lockfile pins unchanged); no extra
models; no deploys or external resources.

## 5. Defaults chosen (where the reviews/contracts left a choice)

- **R1-N1 scope guard**: implemented with a `selectedIdRef` mirror
  (useRef synced by an effect) rather than restructuring state; mutation
  handlers capture the scope at submit time and skip *completion effects*
  (announcement, form close + draft reset, reload, banner, confirm reset)
  when the selection changed. The write itself was already correctly
  scoped and was not touched. `deleteItem` owns its whole error path so
  the row's `onClick` is a single plain call.
- **R1-N5 interface**: additive envelope field `today` + per-item
  `dueState` (server-computed by a pure shared helper) rather than a day
  offset or client-side recomputation — the UI never reads a clock for
  due labels; a per-item `today` is deliberately not added. Test clock:
  `WORKBOARD_FAKE_TODAY` (test-only, real date 2000–2099, invalid ⇒
  fail-fast at startup); pinned e2e day **2026-11-07** (today's date at
  authoring time, inside the seed range + tolerance margins).
- **R1-N6 tie model**: disclose the attainable exception (same-millisecond
  new item whose id sorts after the page-boundary cursor may appear on a
  later page) rather than promise an unattainable full exclusion; the
  walk example carries an observed-clock precondition. Threshold fixed to
  exactly-20 ⇒ `nextCursor: null`.
- **R1-N7 messages**: missing title keeps the byte-identical baseline
  message `title is required.`; empty/non-string gets
  `title must be a non-empty string.`; non-object entries get
  `entry <i>: entry must be a JSON object.` checked before field checks.
- **R1-N8 semantics**: reversion to pristine re-fires the debounce and
  overwrites the draft; a draft is never deleted by reversion.
- **Endpoint manifest**: exported as `r2-endpoint-manifest.json` at the
  workspace root (73 files — the 71 prior paths, 14 of them updated, plus
  the two R2 record files; `review-inputs` session files stay outside the
  source manifests, following R1's convention; the manifest itself lives
  at the root because `review-inputs/` is a read-only mount), so the next
  reviewer can verify this endpoint the same way this session verified
  R1's.

## 6. Substantive edits (actual files changed)

14 of the 71 source files changed; all 57 others bit-identical to the R1
endpoint. Byte sizes are before → after.

| File | Bytes | Change |
| --- | --- | --- |
| `baseline/src/components/Workboard.tsx` | 11084 → 12377 | R1-N1: `selectedIdRef` scope guard; `createItem`/`updateItem`/`deleteItem` capture scope at submit, skip completion effects on selection change; `deleteItem` owns its error path |
| `baseline/e2e/switch.spec.ts` | 3146 → 7377 | R1-N1: new describe "delayed action completion stays scoped to its own workspace" with two held-response regressions (create, delete), each proving the write still lands in its own workspace; file-header contract comment updated |
| `baseline/tests/api/auth.test.ts` | 4732 → 6666 | R1-N2: +3 tests / 2 extended (HEAD-via-GET ×3 cases; Better Auth native 404 GET/POST + app-envelope DELETE; unsupported-method 404 with and without a session). api suite 34 → 36 |
| `baseline/docs/baseline-contract.md` | 17506 → 20127 | §2 browser prerequisite (install AND run variable; install-deps; OS fallback label); §5 route/method precedence at observed granularity; §6 in-flight scope rule + intentional-discard statement; source-inventory path corrected to `../../docs/source-inventory.json` |
| `baseline/README.md` | 2213 → 3230 | R1-N9: `PLAYWRIGHT_BROWSERS_PATH` required for install AND run, both orders, mismatch symptom, install-deps pointer |
| `contracts/S08-due-date-semantics.md` | 6419 → 10647 | R1-N4/N5: full R2 rewrite — envelope `today`, per-item `dueState`, shared pure helper, `WORKBOARD_FAKE_TODAY` fail-fast pin, e2e day 2026-11-07, enumerated labels under the pin, exact permitted migrations |
| `contracts/S03-stable-cursor-pagination.md` | 5679 → 7892 | R1-N6: consistency model (total order; no-repeats with disclosed same-millisecond tie exception; skip tolerance; observed-clock precondition), exact-20/21 acceptance |
| `contracts/S04-transactional-import.md` | 5135 → 6305 | R1-N7: message split + entry-level diagnostics + entry-before-field precedence + examples |
| `contracts/S07-failure-safe-editing.md` | 5741 → 6212 | R1-N8: trigger = changed while form open; pristine reversion overwrites, never deletes |
| `contracts/C1-workspace-item-counts.md` | 3954 → 4575 | R1-N3: revision marker R2; migration list enumerates the 3× `Borealis Ops` and 2× `Apollo Launch` selector-label migrations in switch.spec.ts, assertion-only |
| `contracts/README.md` | 7352 → 7464 | revision marker R2 (title + revision-history paragraph) |
| `docs/faq-draft.md` | 8044 → 9825 | Q13 route/method correction; Q2/Q15/Q16/Q17 consistency updates (browser cache variable, counts, S03/S07/S08 semantics) |
| `docs/source-inventory.json` | 18577 → 19542 | R1-N9: `@playwright/test` entry corrected (host OS unverified; "Ubuntu 24.04" is Playwright's fallback label; install/run cache consistency); revision_note for R2 |
| `README.md` (root) | 1508 → 2266 | rewritten for the R2 endpoint: review-inputs inventory, the root-level `r2-endpoint-manifest.json` bullet, counts 11/36/20, same browser caveat, different-model-review disclaimer |

## 7. Verification record (exact commands and exit codes)

All commands run in `baseline/` unless noted. E2e env for every Playwright
run: `CI=1 PLAYWRIGHT_BROWSERS_PATH=/workspace/.cache/ms-playwright`.

| # | Command | Exit | Notes |
| --- | --- | --- | --- |
| 1 | `npm ci --no-audit --no-fund` | 0 | fresh install from the committed lockfile at session start; pins unchanged |
| 2 | `PLAYWRIGHT_BROWSERS_PATH=/workspace/.cache/ms-playwright npx playwright install chromium --only-shell` | 0 | headless shell into `/workspace/.cache/ms-playwright` (chromium_headless_shell-1254) |
| 3 | `CI=1 PLAYWRIGHT_BROWSERS_PATH=… npm run check:full` (pre-edit) | 0 | clean R1 endpoint: 11 unit / 34 api / 18 e2e — the red→green reference point |
| 4 | red→green: restore pre-fix `Workboard.tsx`, run the 2 new switch tests, re-apply fix | 2 expected failures → pass | test (a) failed at `toHaveValue("Borealis unsaved draft")` (form closed, Title field gone); test (b) failed at `toHaveText("")` (live region announced "Work item deleted.") — Terra's reproduction, via the public suite |
| 5 | `CI=1 PLAYWRIGHT_BROWSERS_PATH=… npm run check:full` (interim) | 0 | 20/20 e2e, both new tests green |
| 6 | `CI=1 PLAYWRIGHT_BROWSERS_PATH=… npm run check:full` (**final**) | **0** | typecheck clean; lint clean; **11/11 unit; 36/36 api (auth 10, items 14, seed 5, workspaces 7); 20/20 e2e (14.8s)**; a second identical run logged to scratch |
| 7 | scratch route probe (`.probe-routes.mts`, run in `baseline/`, removed after) | 0 | R1-N2: HEAD-via-GET statuses/bodies; app-envelope vs Better Auth native 404s — reproduced first-hand before documenting |
| 8 | scratch keyset probe (`.probe-keyset.mts` + `probe.db`, removed after) | 0 | R1-N6: same-millisecond larger-id row appears on page 2; exactly-20 ⇒ null / 21 ⇒ non-null. First probe run had a cursor-binding bug; corrected run is the cited one |
| 9 | `node` JSON parse + validation over `docs/source-inventory.json` | 0 | validity after R2 corrections |
| 10 | grep censuses (switch.spec.ts selector labels; cross-contract sweep) | match | exactly 3× `Borealis Ops` + 2× `Apollo Launch` selectOption labels (R1-N3 enumeration exact); counts/messages/markers consistent across contracts, FAQ, READMEs |
| 11 | tree identity vs `review-inputs/prior-endpoint-manifest.json` (`node crypto`) | match | pre-edit 71/71 per-file match; canonical array hash `35f22c5a…eb4b` reproduced; independent tree `00143dd9…d6c4` reproduced, matching Terra's record |
| 12 | post-R2 tree export → `r2-endpoint-manifest.json` (workspace root) | 0 | 73 files; exported after both R2 records were finalized, so endpoint hashes are not quoted inside them (self-reference avoidance, same as R1); placed at the root because `review-inputs/` is a read-only mount |

The pinned-day label arithmetic (2026-11-12 → "Due in 5 days"; 2026-11-25 →
plain "later" form) was recomputed independently before being written into
S08.

## 8. Diagnostics encountered and resolved

- **S03 probe binding bug**: the first keyset probe bound the cursor
  components to the wrong columns and produced a misleading page-2 result;
  detected by asserting the known page-1 boundary first, corrected, and
  re-run — the corrected probe confirms both the tie behavior and the
  exact-20 threshold. (Recorded rather than hidden; the defect was in the
  probe, not the model.)
- **Playwright cache relocation**: the first e2e attempt without
  `PLAYWRIGHT_BROWSERS_PATH` exited 1 with "Executable doesn't exist"
  (missing `chromium_headless_shell-1254`) — the very failure R1-N9
  documents; fixing the instructions and using the variable for install
  AND run resolved it for every subsequent run.
- **Edit-tool whitespace**: contract sub-bullet indentation is 3 spaces
  (5 for continuations); several edit-tool matches initially failed on
  this and were redone with exact indentation. Cosmetic, no content impact.
- **Scratch probes under `baseline/` as dotfiles**: needed for
  `node_modules` resolution; all removed after use (verified: no `.probe*`
  or `probe.db` files remain in the workspace).

## 9. Unresolved questions (carried forward)

- Revision R2 has **not** been re-reviewed by any second session;
  self-review was explicitly not performed. A fresh different-model review
  is required before any qualification step.
- S03: fully excluding mid-walk new items would need extra server state
  (walk-start watermark); the disclosed tie exception is the attainable
  policy until a coordinator chooses otherwise.
- S08: the additive `today`/`dueState` wire change and the
  `WORKBOARD_FAKE_TODAY` pin are contract-only until an S08 task run
  implements and verifies them.
- The two new switch regressions depend on the documented e2e execution
  order (alphabetical spec order; the first switch describe runs before
  the new one). Order-independence was not required and not implemented.
- Better Auth internals beyond the verified paths remain undocumented
  (FAQ open question, carried from R1).
- Scoring weights, corpus packaging, and qualification remain
  coordinator-owned.
- Playwright's OS-fallback warning behavior may differ on other platforms;
  the host OS stays unverified.

## 10. What remains unqualified / explicitly not done

- No reference solutions, sealed acceptance tests, or oracles exist or are
  claimed; the fixture's deliberately missing task features stay missing.
- No calibration runs, no study models executed against the contracts.
- No new npm dependencies; lockfile and `package.json` scripts unchanged.
- No databases beyond disposable local SQLite probes; no production
  resources, deploys, or pushes.
- Endpoint reached: revised source tree (14 files changed, 57 untouched)
  + final green full check + `REPAIR_DISPOSITIONS_R2.json` +
  `REPAIR_PROVENANCE_R2.md` + `r2-endpoint-manifest.json` (workspace
  root).
  The session stopped here — **before cross-reviewing or approving its
  own revision**, per instructions. The final check:full ran on the
  completed `baseline/` tree (all baseline edits and both new e2e tests
  included); after it, only the root `README.md` review-inputs bullet
  (a workspace-level file the check does not read), the two R2 record
  files, and the endpoint manifest were written. The endpoint manifest's
  hashes are the revision's identity and cover all of those final bytes.
