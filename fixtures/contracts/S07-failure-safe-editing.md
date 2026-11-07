# S07 — Failure-safe editing: draft survival and recovery

- Status: DRAFT, revision R2 (not qualified)
- Kind: scored
- Area: recovery after failed saves
- Conflicts with: S10 (workspace-switch guard) — S07 covers reload/crash
  survival of a single form; S10 covers unsaved-state on workspace switch.
  Independent on the baseline, never combined (reset-per-task policy in
  `README.md`).

## Baseline behavior (explicit, documented limitation)

On a failed create/edit save the form stays open, the input is preserved,
and the error shows in `role="alert"`. But:
- a **page reload discards the draft** (no persistence),
- there is **no retry affordance** (the user must re-submit manually — which
  baseline already permits — and no indication the draft is at risk),
- there is no distinction between "network down" and "server rejected".

## Requirement

Make editing failure-safe end to end:

1. **Draft persistence (per form slot)**: while a create or edit form is
   open, every value change schedules a debounce-save (≤500 ms after the
   last change) of the current values to `sessionStorage` keyed
   `workboard.draft.<workspaceId>.<create|itemId>`. The trigger is "the
   form is open and its values changed", **not** "the values differ from
   the pristine state": a change that edits a field — and a later change
   that returns the values to pristine (create defaults / the loaded
   item's values; "changed", not "non-empty": a field cleared back to
   empty is a legitimate in-progress state) — each (re)fires the debounce
   and overwrites the stored draft. An untouched form never writes a
   draft. A draft stores `{ savedAt, values }` (values = the form fields).
   The pending debounce timer is canceled when the form is closed without
   saving (Cancel/close) — the draft saved by the *last* fired debounce
   remains until explicitly cleared as below. Successful save OR explicit
   Cancel removes the draft. Sign out removes all `workboard.draft.*`
   keys.
2. **Draft restore (disclosed, automatic)**: if a draft exists when the
   form opens, the fields are prefilled from it **automatically** — there
   is no confirmation dialog; the disclosure IS the info banner
   (`role="status"`) with text exactly `Draft restored.`, and the saved
   time is exposed in the banner's `title` attribute only (keeps e2e
   deterministic). Cancel/Save clears the draft.
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
- ada types a title, waits, then clears the Title field completely and
  waits → the reversion is itself a change: the debounce fires again and
  overwrites the earlier draft (which had stored the typed title) with the
  cleared values; a reload restores the cleared state with the banner.
  Returning to pristine never deletes the draft and never leaves the stale
  typed title behind.
- Simulated failure (e2e route-aborts `PATCH /api/items/*`): edit an item →
  alert starts with `Network problem — `, "Retry save" visible; un-abort,
  click "Retry save" → item updated with the same values, form closes.
- Double-click protection: route-delayed PATCH + double click "Save
  changes" → exactly one PATCH request observed.

## Boundaries & non-goals

- No localStorage (sessionStorage only), no cross-tab sync, no draft for
  the workspace-creation form, no autosave to the server.
- **Stale-draft boundaries (disclosed)**: if the item behind an edit draft
  is deleted, the draft key simply stays until overwritten or sign-out
  cleanup; a stale key is never restored into a form for a non-existent
  item (the edit form cannot open for it) and never crashes the app. No
  other garbage collection is required.
- **Composability boundary (disclosed)**: drafts are keyed per workspace
  and survive workspace switches and reloads within the same tab session
  (that is the feature). The switch-moment guard is S10's separate
  increment and is NOT implemented here; switching away with a dirty form
  still discards the *live form* exactly as baseline — the sessionStorage
  draft is what persists, and it restores when the same slot reopens.
- No offline queue/sync; "Retry save" is a single immediate re-submit.
- Do not change server behavior or API shapes.

## Compatibility expectations

- Baseline failure display (form stays open, alert shown) remains.
- `npm run check:full` green (no baseline test edits).

## Ownership

- Owns: draft-store helper (pure, unit-tested with injected storage),
  ItemForm integration (debounce + restore + retry), e2e tests using
  Playwright route interception for the failure cases.
- Must not touch: API, schema, seed, auth.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| Draft round-trip | e2e: type → wait → reload → values restored + `Draft restored.` banner; key removed after save/cancel |
| Cleared-field draft | e2e: type, clear title, wait → draft stores cleared values; reload restores them |
| Failure prefix + retry | e2e: aborted request → `Network problem — ` alert + Retry button → success after un-abort |
| Values preserved on failure | e2e: field values unchanged after failed save |
| Single request | e2e: delayed route + double click → 1 PATCH |
| Cleanup | unit test: save/cancel/sign-out remove keys; malformed draft ignored; stale deleted-item draft never crashes |
