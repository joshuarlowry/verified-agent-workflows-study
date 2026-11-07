# S10 — Workspace-switch guard for unsaved input

- Status: DRAFT, revision R1 (not qualified)
- Kind: scored
- Area: dependent UI state
- Conflicts with: S07 (draft persistence across reload — different store and
  trigger), C4 (last-workspace restore — composes but independent).
  Independent on the baseline, never combined (reset-per-task policy in
  `README.md`).

## Baseline behavior (explicit)

Switching workspaces (or closing the new-item form) **silently discards**
any in-progress input: the create form's text, an open edit form's changes —
all lost without warning. Baseline selection effect resets `editingId`,
`createOpen`, and errors on switch (that reset is the documented baseline
behavior).

## Requirement

Protect unsaved input during workspace switches:

1. **Dirty detection (exact)**: a form is "dirty" when its current values
   differ from its pristine state, compared field by field:
   - create form: pristine = the form's defaults (`title:""`, `notes:""`,
     `status:"open"`, `dueDate:""`). Dirty ⇔ any field differs (e.g. title
     typed, a note typed, status moved off Open, or a date picked).
   - edit form: pristine = the loaded item's values (`dueDate` normalized
     the same way the form loads it: empty string for none). Dirty ⇔ any
     field differs from the loaded values. An edit form opened and left
     untouched is pristine even though its fields are non-empty.
2. **Switch guard**: when the user changes the workspace select while a form
   is dirty, the switch is **held**: the list and selector keep the current
   workspace, and a confirmation bar appears (focus-visible):
   - text (exact): `Unsaved changes in "<form title>". Switching workspaces
     will discard them.` where `"<form title>"` is exactly
     `New work item` for the create form and the item's current title for
     an edit form (e.g. `Unsaved changes in "Prepare demo script".
     Switching workspaces will discard them.`) — machine-checkable prefix
     `Unsaved changes in` + exact suffix `Switching workspaces will discard
     them.`
   - buttons **"Discard and switch"** (proceeds: switches, drops form
     state) and **"Keep editing"** (stays).
   - The pending selection is not applied until "Discard and switch".
3. **Non-guarded resets**: switching with a pristine/open (not dirty) form
   behaves exactly as baseline (instant switch, forms closed).
4. **No guard for other actions**: closing the form via Cancel/Close and the
   two-step delete confirm keep baseline behavior (explicit user actions
   that already imply discarding).
5. Focus management (minimal): when the bar appears, focus moves to
   "Keep editing"; Escape key = "Keep editing".

## Public examples

- bruno opens "New work item", types "Ghost draft", selects "Borealis Ops"
  → no switch happens; bar appears with text `Unsaved changes in "New work
  item". Switching workspaces will discard them.`; "Keep editing" → stays
  on Apollo, form still has "Ghost draft". "Discard and switch" → Borealis
  selected, form closed, "Ghost draft" nowhere.
- bruno opens edit for "Prepare demo script" (an Apollo item he may edit),
  changes nothing, selects Borealis → instant baseline switch (no bar).
- bruno opens edit for "Prepare demo script", changes notes only → selects
  Borealis → bar with `Unsaved changes in "Prepare demo script". …`;
  Escape → stays.
- A create form with only the status select moved to "Done" (no text typed)
  is dirty → the guard applies.

## Boundaries & non-goals

- No beforeunload/`pagehide` guard (browser-level), no draft persistence
  (S07), no multi-form guards, no guard when deleting/confirming delete, no
  toast variants.
- The guard does not apply to sign-out (out of scope).
- Disclosed boundary: dirty comparison is exact string/value equality
 (no trimming, no case folding — even if S01-style trimming existed, this
  task is defined against the baseline); only workspace-select changes are
  guarded.

## Compatibility expectations

- Non-dirty switching remains instant and identical to baseline (existing
  e2e switch tests keep passing untouched).
- `npm run check:full` green (no baseline test edits).

## Ownership

- Owns: dirty-tracking (pure comparator + unit tests), pending-selection
  state machine in `Workboard.tsx`, guard bar component + minimal CSS +
  focus/Escape handling, e2e tests (both branches + Escape).
- Must not touch: API, schema, auth, delete confirm flow, C4-style storage.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| Guard on dirty | e2e: typed draft + select switch → bar with exact text; selection unchanged |
| Exact form titles | e2e: create-form bar names `New work item`; edit-form bar names the item title |
| Discard branch | e2e: "Discard and switch" → new workspace + form gone |
| Keep branch | e2e: "Keep editing"/Escape → same workspace + draft intact |
| Pristine pass-through | e2e: untouched open form + switch → immediate switch, no bar |
| Status-only dirty | e2e: status moved off Open with no text → guard applies |
| Focus | e2e: "Keep editing" focused when bar opens |
