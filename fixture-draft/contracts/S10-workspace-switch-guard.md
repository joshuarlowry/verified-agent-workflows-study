# S10 — Workspace-switch guard for unsaved input

- Status: DRAFT (not qualified)
- Kind: scored
- Area: dependent UI state
- Conflicts with: S07 (draft persistence across reload — different store and
  trigger), C4 (last-workspace restore — composes but independent).
  Independent on the baseline.

## Baseline behavior (explicit)

Switching workspaces (or closing the new-item form) **silently discards**
any in-progress input: the create form's text, an open edit form's changes —
all lost without warning. Baseline selection effect resets `editingId`,
`createOpen`, and errors on switch (that reset is the documented baseline
behavior).

## Requirement

Protect unsaved input during workspace switches:

1. **Dirty detection**: a create form or edit form is "dirty" when any field
   differs from its pristine state (create: any non-empty field; edit: any
   field differing from the loaded item).
2. **Switch guard**: when the user changes the workspace select while a form
   is dirty, the switch is **held**: the list and selector keep the current
   workspace, and a confirmation bar appears (focus-visible):
   - text (exact): `Unsaved changes in "<form title>". Switching workspaces
     will discard them.` — machine-checkable prefix `Unsaved changes in` +
     exact suffix `Switching workspaces will discard them.`
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

- ada opens "New work item", types "Ghost draft", selects "Borealis Ops" →
  no switch happens; bar appears with exact text; "Keep editing" → stays on
  Apollo, form still has "Ghost draft". "Discard and switch" → Borealis
  selected, form closed, "Ghost draft" nowhere.
- ada opens edit for "Prepare demo script", changes nothing, selects
  Borealis → instant baseline switch (no bar).
- ada opens edit and changes notes → switch → bar; Escape → stays.

## Boundaries & non-goals

- No beforeunload/`pagehide` guard (browser-level), no draft persistence
  (S07), no multi-form guards, no guard when deleting/confirming delete, no
  toast variants.
- The guard does not apply to sign-out (out of scope).

## Compatibility expectations

- Non-dirty switching remains instant and identical to baseline (existing
  e2e switch tests keep passing untouched).
- `npm run check:full` green.

## Ownership

- Owns: dirty-tracking (pure comparator + unit tests), pending-selection
  state machine in `Workboard.tsx`, guard bar component + minimal CSS +
  focus/Escape handling, e2e tests (both branches + Escape).
- Must not touch: API, schema, auth, delete confirm flow, C4-style storage.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| Guard on dirty | e2e: typed draft + select switch → bar with exact text; selection unchanged |
| Discard branch | e2e: "Discard and switch" → new workspace + form gone |
| Keep branch | e2e: "Keep editing"/Escape → same workspace + draft intact |
| Pristine pass-through | e2e: untouched open form + switch → immediate switch, no bar |
| Focus | e2e: "Keep editing" focused when bar opens |
