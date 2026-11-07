# S15 — Keyboard quick-add and focus management

- Status: DRAFT, revision R1 (not qualified)
- Kind: scored
- Area: a11y/UX
- Conflicts with: C3 (share links), S10 (switch guard) — different surfaces.
  Independent on the baseline, never combined (reset-per-task policy in
  `README.md`).

## Baseline behavior

No keyboard shortcuts exist. The baseline **is** keyboard-operable: all
buttons and form fields are reachable via Tab and submit works via Enter —
but there is no shortcut to open quick-add, no managed focus placement, and
no focus return. Opening "New work item" leaves focus wherever it was (the
toggling button); closing the form likewise. Announcements use the existing
visually-hidden `role="status"` region.

## Requirement

Add keyboard-first creation affordances with proper focus management:

1. **Quick-add shortcut**: pressing `n` (no modifier) while the workspace
   view is active and the create form is closed opens the create form and
   moves focus into the Title field. The shortcut must NOT fire while focus
   is inside any input/select/textarea (or a `contenteditable`), and must
   ignore repeated/modified keys (`n` with ctrl/alt/meta does nothing).
2. **Submit shortcut**: `Ctrl+Enter` inside the create/edit form submits it
   (equivalent to clicking the primary button; same validation and error
   paths).
3. **Escape closes**: `Escape` inside the create or edit form closes it
   (equivalent to Cancel — no confirm; this is an explicit discard).
4. **Focus return**: after the create form closes (success or Escape/cancel)
   focus returns to the "New work item" toggle button; after an **edit**
   form closes (save success, Escape, or Cancel) focus returns to that
   row's **"Edit"** button (aria-label `Edit <title>`).
5. **Announcements**: reuse the live region: opening quick-add announces
   `New item form opened.`; Escape-close announces `Form closed without
   saving.` (only for Escape, not for Cancel clicks).
6. A small **visible** hint line under the list header:
   `Press N for quick add.` (`<p class="keyboard-hint">`).

## Public examples

- ada signs in, presses `n` → create form opens, Title focused, live region
  announces `New item form opened.`; types a title, `Ctrl+Enter` → item
  created, form closed, focus on "New work item".
- Focus inside Notes, press `n` → nothing happens (no form toggle).
- Open edit for "Prepare demo script", press Escape → form closes, focus is
  on that row's Edit button, live region announces
  `Form closed without saving.`.

## Boundaries & non-goals

- No command palette, no shortcut customization, no other shortcuts, no
  global hotkey help modal, no focus-trap library (inline forms don't
  trap), no changes to the two-step delete or guard logic.

## Compatibility expectations

- All existing interactions keep working; mouse flows unchanged.
- `npm run check:full` green (the new e2e keyboard tests must be robust to
  focus timing).

## Ownership

- Owns: keyboard handler hook (unit-testable pure "should handle" logic +
  integration in `Workboard.tsx`), focus return wiring in
  `ItemForm`/`Workboard`, hint line + minimal CSS, e2e keyboard tests
  (`page.keyboard`).
- Must not touch: API, schema, auth, delete confirm, other forms' behavior.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| Shortcut opens + focuses | e2e: press `n` → form visible + Title focused + announcement |
| Typing-context guard | e2e: focus in Notes + `n` → no toggle |
| Ctrl+Enter submit | e2e: creates item like the button does |
| Escape close + focus return | e2e: edit form Escape → closed, row Edit button focused, announcement |
| Focus return after create | e2e: after successful create, "New work item" focused |
