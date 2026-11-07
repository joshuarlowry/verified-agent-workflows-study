# S11 — Multi-select bulk status update

- Status: DRAFT (not qualified)
- Kind: scored
- Area: batch operations + dependent UI state
- Conflicts with: S02 (archive) and S12 (history) — both optional
  interactions are explicitly out of scope here. Independent on the baseline.

## Baseline behavior

No selection state exists; status changes happen one item at a time via the
edit form. Any member may update any item (baseline rule).

## Requirement

Add checkbox selection and a bulk status action:

1. Each item card (non-edit mode) gains a leading checkbox labeled
   `"Select <title>"`; a header checkbox `"Select all visible items"`
   (indeterminate state when partially selected). Selection is client state,
   cleared on workspace switch or reload (no persistence).
2. When ≥1 selected, an action bar appears above the list:
   `<n> selected` text, a status `<select aria-label="Set status">` with the
   three labels, and button **"Apply to selected"**.
3. API: `POST /api/workspaces/:id/items/bulk-status`, body
   `{ "itemIds": ["…"], "status": "open|in_progress|done" }` (member):
   - validates: array 1–100, all ids must exist **in this workspace**,
     status enum → otherwise 400 `validation_failed` (fields.itemIds /
     fields.status). Unknown id → `fields.itemIds = "item <id> not found in
     this workspace."` (first offender).
   - applies in one transaction: each row's `status` set, `version + 1`,
     `updated_at = now` (even if the status is unchanged — a bulk touch is a
     change). Response `200 { updated: <n>, items: [<WorkItem>…] }` in the
     **request order** of itemIds.
   - all-or-nothing: one bad id → nothing modified.
4. UI apply: calls the endpoint with the selected ids; announces
   `<n> work items updated.` in the live region; clears selection; reloads
   the list.

## Public examples

- Select wi_101 + wi_103, set "Done", apply → 200 `updated: 2`; fresh
  connection: both rows `status='done'`, `version` +1 each, identical
  `updated_at`.
- `{itemIds:["wi_101","wi_missing"]}` → 400, exact first-offender field
  message, **no** rows touched (wi_101 version unchanged).
- UI: three selected, header checkbox indeterminate; select-all → all
  checked; apply "In progress" → announcement `2 work items updated.` (n
  matches), selection cleared.

## Boundaries & non-goals

- No bulk delete/archive (S02/S06 remain single-item), no bulk title/notes
  edits, no cross-workspace selection, no undo.
- No change to single-item PATCH semantics.

## Compatibility expectations

- Baseline list/edit behavior unchanged; selection is additive UI.
- `npm run check:full` green.

## Ownership

- Owns: selection state + action bar UI (Workboard), bulk endpoint +
  transaction in `server/api.ts`, api tests (validation/transaction/order)
  + e2e (select/indeterminate/apply/announcement).
- Must not touch: schema, auth, seed, delete flow.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| Bulk endpoint | api test: 2 ids → both updated in one transaction, response in request order |
| All-or-nothing | api test: one bad id → 400 exact message; other rows untouched |
| Validation | api tests: empty/oversized array, bad status, foreign-workspace id |
| Version/updated_at | api test: version+1 and equal updated_at on both rows |
| UI | e2e: selection → indeterminate → apply → announcement + cleared selection + reloaded statuses |
