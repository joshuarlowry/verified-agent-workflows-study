# Workboard Lab — Frozen Product FAQ (DRAFT)

Status: **draft, pre-review**. Answers here settle material defaults for all
task contracts neutrally (no model-specific tailoring). Once reviewed, this
file should be frozen as the product-FAQ part of the task corpus.

---

## Settled defaults

**Q1. Does the baseline trim or length-limit titles/notes?**
No. Baseline stores strings verbatim; the only title rule is "non-empty
string". Any trimming/limits are task territory and must be additive with
documented behavior changes.

**Q2. How are dates handled?**
`dueDate` is an opaque `YYYY-MM-DD` string (shape-validated) or `null`. The
baseline does no calendar-date validation, no comparisons, and displays the
raw string. Timestamps are ISO-8601 UTC strings. Timezone-safe calendar
semantics are task territory.

**Q3. Why 404 and not 403 for non-members?**
Baseline anti-enumeration rule: unknown workspace/item and "exists but you
are not a member" are indistinguishable (404 `not_found`). Task contracts may
change this only if they say so explicitly.

**Q4. What happens when two people edit the same item?**
Baseline is last-write-wins: PATCH never rejects for concurrency and ignores
any client-supplied version hints (there is no such field in the request
contract; `version` is response-only metadata that increments on every
successful PATCH).

**Q5. Is deletion soft or hard?**
Hard `DELETE` (row removed, 204, no trash/restore). Archive/restore features
do not exist in the baseline.

**Q6. Who may mutate items?**
Any authenticated member of the item's workspace. The workspace `owner` role
currently grants no additional powers (documented baseline gap; ownership
tightening is task territory, not an implied rule).

**Q7. May an implementing agent add npm dependencies?**
Avoid it. If genuinely necessary: exact-pinned, justify in the task notes,
no new runtime services (no hosted deps, no DB servers beyond the local
SQLite file), and `npm run check:full` must still pass.

**Q8. Where do databases and ports live?**
DB: any path via `WORKBOARD_DB` (defaults `data/workboard.db`; e2e uses
`.tmp/e2e.db`). Both are git-ignored and disposable. API default port 4310
(8787 collides with the study sandbox harness); e2e serves on 4599; Vite dev
UI on 5173.

**Q9. Session lifetime?**
Baseline does not configure expiry; Better Auth 1.7.18 defaults apply and
sessions are validated per request. Tests must not depend on specific
expiry values.

**Q10. Is the seed fully deterministic?**
IDs, emails, names, memberships, items and pinned timestamps are fixed.
Better Auth user rows (ids, password hashes) are library-generated per reset;
nothing in the baseline orders by user id, so list behavior stays
deterministic. Sign-in credentials are public (baseline contract §4).

**Q11. Can agents change baseline tests or the baseline contract?**
No. Baseline tests are regression guards and must remain green. New tests
are added alongside. The baseline contract is frozen; task contracts define
additions/changes on top of it.

**Q12. UI stack rules?**
React + plain CSS only. No component libraries, no CSS frameworks, no icon
or font assets, no UI rewrites of existing screens.

**Q13. Error shape changes?**
The `{ "error": { code, message, fields? } }` envelope and existing codes are
stable. New codes/fields may be added if a task contract defines them;
existing codes keep their meaning.

**Q14. Schema changes in tasks?**
Additive DDL (new columns/tables, idempotent `CREATE ... IF NOT EXISTS`
style) is allowed where a contract requires it. Destructive changes to
baseline tables/columns are not allowed unless the contract mandates an
explicit migration path.

**Q15. Does the baseline include pagination, search, filters?**
No. `GET .../items` returns all items ordered `updated_at DESC, id ASC`.

## Questions that cannot be settled honestly at this stage

1. **Combined-task behavior.** Contracts are written to be independently
   implementable against this baseline. If multiple tasks are ever applied to
   the same evolving codebase in sequence, interaction effects (e.g. S03
   pagination × S02 archive filters) cannot be guaranteed from the contracts
   alone. The coordinator must decide whether scored runs reset to baseline
   per task.
2. **Better Auth 1.7.18 undocumented internals.** Verified behaviors are
   recorded in `docs/source-inventory.json`; anything beyond the verified
   paths (advanced cookie/session config, internal error taxonomy beyond
   observed statuses) cannot be answered from documentation alone.
3. **Scoring rubric weights.** The fixture defines observable acceptance
   mappings, not grade weights; assigning weights is a coordinator decision
   outside this preparation phase.
4. **Corpus packaging.** The identical approved corpus for all scored agents
   will be supplied by the coordinator; this repo cannot vouch for what the
   final corpus will include beyond these files.
