# Workboard Lab — Frozen Product FAQ (DRAFT, revision R1)

Status: **draft, repaired, pre-review**. Answers here settle material
defaults for all task contracts neutrally (no model-specific tailoring).
Revision R1 reconciles this FAQ with the repaired baseline
(`baseline/docs/baseline-contract.md`) and the revised contracts. Once
reviewed, this file should be frozen as the product-FAQ part of the task
corpus.

---

## Settled defaults

**Q1. Does the baseline trim or length-limit titles/notes?**
No. Baseline stores strings verbatim; the only title rule is "non-empty
string". Any trimming/limits are task territory and must be additive with
documented behavior changes (S01 defines exactly that change).

**Q2. How are dates handled?**
`dueDate` is an opaque `YYYY-MM-DD` string (shape-validated) or `null`. The
baseline does no calendar-date validation, no comparisons, and displays the
raw string. Timestamps are ISO-8601 UTC strings. Timezone-safe calendar
semantics are task territory (S08), which defines a server→client day
interface (envelope `today` + per-item `dueState`) and pins a test-only
server day (`WORKBOARD_FAKE_TODAY`) so every e2e/api date expectation is
exact and clock-independent (see S08's testing policy).

**Q3. Why 404 and not 403 for non-members?**
Baseline anti-enumeration rule: unknown workspace/item and "exists but you
are not a member" are indistinguishable (404 `not_found`). Task contracts may
change this only if they say so explicitly.

**Q4. What happens when two people edit the same item?**
Baseline is last-write-wins: PATCH never rejects for concurrency and ignores
any client-supplied version hints (there is no such field in the request
contract; `version` is response-only metadata that increments on every
successful PATCH). S09 adds an optional, explicitly typed conflict flow.

**Q5. Is deletion soft or hard?**
Hard `DELETE` (row removed, 204, no trash/restore). Archive/restore features
do not exist in the baseline (S02 adds them additively).

**Q6. Who may mutate items?**
Any authenticated member of the item's workspace. The workspace `owner` role
currently grants no additional powers (documented baseline gap; ownership
tightening is task territory — S06 — not an implied rule).

**Q7. May an implementing agent add npm dependencies?**
Avoid it. If genuinely necessary: exact-pinned, justify in the task notes,
no new runtime services (no hosted deps, no DB servers beyond the local
SQLite file), and `npm run check:full` must still pass.

**Q8. Where do databases and ports live?**
DB: any path via `WORKBOARD_DB` (defaults `data/workboard.db`; e2e uses
`.tmp/e2e.db`). Both are git-ignored and disposable. Only new local
disposable SQLite files are authorized — no other databases or external
resources. API default port 4310 (8787 collides with the study sandbox
harness); e2e serves on 4599; Vite dev UI on 5173.

**Q9. Session lifetime?**
Baseline does not configure expiry; Better Auth 1.7.18 defaults apply and
sessions are validated per request. Tests must not depend on specific
expiry values.

**Q10. Is the seed fully deterministic?**
IDs, emails, names, memberships, items and pinned timestamps are fixed.
Better Auth user rows (ids, password hashes) are library-generated per reset;
nothing in the baseline orders by user id, so list behavior stays
deterministic. Sign-in credentials are public (baseline contract §4).

**Q11. May agents change baseline tests or the baseline contract?**
Baseline tests are regression guards: by default they must not be changed,
deleted, or weakened — new tests go alongside. A task contract may permit
**enumerated, expectation-only migrations** to specific public assertions
that its requirement makes obsolete (exact files/assertions listed in the
contract; equivalent behavioral coverage preserved; every migration recorded
by the implementer). Contract-specific enumerations win for their scope;
this rule fills the gaps. The baseline **contract** is never edited by a
task.

**Q12. UI stack rules?**
React + plain CSS only. No component libraries, no CSS frameworks, no icon
or font assets, no UI rewrites of existing screens.

**Q13. Error shape changes?**
The `{ "error": { code, message, fields? } }` envelope and existing codes are
stable for Workboard endpoints, and `error.fields` values are always
**strings**. New codes/fields may be added if a task contract defines them.
Two documented facts reconcile wording with observed behavior: (1) unknown
endpoints — and non-HEAD methods with no matching route on known paths —
return 404 `not_found` in the app envelope regardless of session state
(route resolution precedes authentication; verified with and without a
session). Hono dispatches HEAD through matching GET handlers, but the handler
sees HEAD and its status need not equal GET: `HEAD /api/health` → 200,
unauthenticated `HEAD /api/me` → 401, unknown HEAD → 404, and unauthenticated
`GET /api/auth/get-session` → 200 JSON null versus HEAD → 404. HEAD bodies
are empty; (2) Better Auth routes (`/api/auth/*`, mounted for POST and GET)
use Better Auth's native responses, not the app envelope (observed: wrong
credentials → 401 `{"message":"Invalid email or password","code":"INVALID_EMAIL_OR_PASSWORD"}`;
unknown auth sub-routes on GET/POST → Better Auth's own 404 with an empty
body; HEAD reaches the GET mount with method HEAD; other non-HEAD methods,
e.g. DELETE, match no handler → the app 404 envelope). The baseline does not
normalize Better Auth responses.
The only task-defined non-string exception to date is S09's
`error.currentItem` (a typed additive field; `error.fields` stays
string-valued).

**Q14. Schema changes in tasks?**
Additive DDL (new columns/tables, idempotent `CREATE ... IF NOT EXISTS` /
guarded `ALTER TABLE ADD COLUMN` style) is allowed where a contract requires
it. Destructive changes to baseline tables/columns are not allowed unless
the contract mandates an explicit migration path.

**Q15. Does the baseline include pagination, search, filters?**
No. `GET .../items` returns all items ordered `updated_at DESC, id ASC`.
S03/S02 add pagination/filters as separate increments with explicitly
disclosed consistency models (S03: strict live keyset, no snapshot; a
write strictly newer than the current cursor stays out of remaining pages,
while equal-key ties or older writes, including future-dated stored rows,
can cause repeats or new items to appear; exactly-20-item workspaces get
`nextCursor: null` at the default limit).

**Q16. What happens to the item list during a workspace switch?**
The previous workspace's items are dropped immediately: the list never
renders another workspace's rows or row actions — while the next load is
delayed it shows the loading state, and if it fails it shows the error
banner + "Retry" with the old data still gone (regression-covered by
`e2e/switch.spec.ts`). A mutation's **late completion** is also
scope-guarded: the request targets its original workspace, but success or
failure effects belong to its selection lifetime (including ABA returns)
and, for forms or delete confirmation, to the original form/action. A
successful write persists; a failure need not. Held responses cannot alter
later forms, feedback, pending flags or confirmation (covered by
`e2e/switch.spec.ts` and `e2e/isolation.spec.ts`). The *silent discard of unsaved form input* on switch
is intentionally still baseline behavior (S10 builds the guard; S07 builds
sessionStorage draft survival — separate increments, never combined).

**Q17. Do I need to install anything besides `npm ci`?**
Yes, for e2e: the Playwright chromium headless shell
(`npx playwright install chromium --only-shell`). By default it installs
into and is read back from the user cache, so the plain install works when
`HOME` is writable and stable. If you relocate the cache with
`PLAYWRIGHT_BROWSERS_PATH`, the SAME variable must be set for both the
install and every test run — otherwise the run looks in the default cache,
finds no browser, and exits 1 ("Executable doesn't exist"). The headless
shell also needs chromium's shared libraries (NSS, fontconfig, …); if a
launch fails with missing libraries, run `npx playwright install-deps
chromium`. `@playwright/test` 1.65.0 does not ship browsers with the npm
install. The e2e server is never reused (`reuseExistingServer:
false`): each run owns a freshly reset `.tmp/e2e.db` on 127.0.0.1:4599; a
foreign listener there fails the run loudly.

**Q18. Does each task run against a fresh baseline?**
Yes (settled at R1). Every calibration/scored task starts from a freshly
reset baseline (fresh tree + `npm run db:reset` on a disposable SQLite
file). No contract may assume another task's changes; combined-task behavior
is undefined and must never be asserted by acceptance checks. Final corpus
packaging remains a coordinator decision, but this reset policy is the
preparation-phase default baked into every contract.

## Questions that cannot be settled honestly at this stage

1. **Better Auth 1.7.18 undocumented internals.** Verified behaviors are
   recorded in `docs/source-inventory.json`; anything beyond the verified
   paths (advanced cookie/session config, internal error taxonomy beyond
   observed statuses) cannot be answered from documentation alone.
2. **Scoring rubric weights.** The fixture defines observable acceptance
   mappings, not grade weights; assigning weights is a coordinator decision
   outside this preparation phase.
3. **Corpus packaging.** The identical approved corpus for all scored agents
   will be supplied by the coordinator; this repo cannot vouch for what the
   final corpus will include beyond these files.
4. **Post-revision qualification.** Every revised contract (R1) still needs
   independent cross-review, then reference implementations and sealed
   tests, before any scored use. Nothing in this workspace asserts those
   steps are done.
