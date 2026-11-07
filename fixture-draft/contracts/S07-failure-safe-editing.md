# S07 — Failure-safe editing: draft survival and recovery

- Status: DRAFT (not qualified)
- Kind: scored
- Area: recovery after failed saves
- Conflicts with: S10 (workspace-switch guard) — S07 covers reload/crash
  survival of a single form; S10 covers unsaved-state on workspace switch.
  Independent on the baseline.

## Baseline behavior (explicit, documented limitation)

On a failed create/edit save the form stays open, the input is preserved,
and the error shows in `role="alert"`. But:
- a **page reload discards the draft** (no persistence),
- there is **no retry affordance** (the user must re-submit manually — which
  baseline already permits — and no indication the draft is at risk),
- there is no distinction between "network down" and "server rejected".

## Requirement

Make editing failure-safe end to end:

1. **Draft persistence (per form slot)**: while a create or edit form has a
   non-empty, changed value, debounce-save (≤500 ms after last keystroke) a
   draft to `sessionStorage` keyed
   `workboard.draft.<workspaceId>.<create|itemId>`. A draft stores
   `{ savedAt, values }` (values = the form fields). Successful save OR
   explicit Cancel removes the draft. Sign out removes all
   `workboard.draft.*` keys.
2. **Restore with consent**: if a draft exists when the form opens, the
   fields are prefilled from it and the form shows an info banner
   (`role="status"`) with text exactly `Draft restored.`; the saved time is
   exposed in the banner's `title` attribute only (keeps e2e deterministic).
   Cancel/Save clears the draft.
3. **Failure recovery**: when a save fails:
   - the form stays open with values preserved (baseline behavior kept),
   - the alert message gains a **"Retry save"** button that re-submits the
     same values without user edits (a distinct button, not the submit),
   - the alert distinguishes transport vs server errors: text prefix
     `Network problem — ` for fetch/type failures (TypeError/offline),
     otherwise the server message as today.
4. **Guard against double-submit**: while a save or retry is in flight, both
   buttons are disabled (`busy` state), and a second Enter keypress does not
   fire a duplicate request.

## Public examples

- ada types "Quarterly plan review" + notes in the create form, waits ~1s,
  reloads the page → form (or its reopened state after clicking "New work
  item") prefilled with the draft; banner `Draft restored.`; after a
  successful create the sessionStorage key is gone.
- Simulated failure (e2e route-aborts `PATCH /api/items/*`): edit an item →
  alert starts with `Network problem — `, "Retry save" visible; un-abort,
  click "Retry save" → item updated with the same values, form closes.
- Double-click protection: route-delayed PATCH + double click "Save
  changes" → exactly one PATCH request observed.

## Boundaries & non-goals

- No localStorage (sessionStorage only), no cross-tab sync, no draft for
  the workspace-creation form, no autosave to the server, no draft for
  deleted items (if the item is deleted, the edit draft is stale — clearing
  it on reload is acceptable and must not crash).
- No offline queue/sync; "Retry save" is a single immediate re-submit.
- Do not change server behavior or API shapes.

## Compatibility expectations

- Baseline failure display (form stays open, alert shown) remains.
- `npm run check:full` green.

## Ownership

- Owns: draft-store helper (pure, unit-tested with injected storage),
  ItemForm integration (debounce + restore + retry), e2e tests using
  Playwright route interception for the failure cases.
- Must not touch: API, schema, seed, auth.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| Draft round-trip | e2e: type → wait → reload → values restored + `Draft restored.` banner; key removed after save/cancel |
| Failure prefix + retry | e2e: aborted request → `Network problem — ` alert + Retry button → success after un-abort |
| Values preserved on failure | e2e: field values unchanged after failed save |
| Single request | e2e: delayed route + double click → 1 PATCH |
| Cleanup | unit test: save/cancel/sign-out remove keys; malformed draft ignored |
