# S01 — Input validation hardening: trim, limits, field errors

- Status: DRAFT (not qualified)
- Kind: scored
- Area: validation (API + UI)
- Conflicts with: S09 (both touch PATCH semantics — different fields), S08
  (due-date rules — this task must not add date logic).

## Baseline behavior (explicit, from the frozen baseline)

- `title`: any non-empty string, stored **verbatim** (`"  padded title  "`
  round-trips exactly; whitespace-only `"   "` is accepted).
- No length caps on `title`/`notes` (a 10k-char title is accepted).
- Validation failures return `400 {error:{code:"validation_failed",
  message:"Invalid work item input.", fields:{...}}}` only when a field is
  missing or of the wrong type; the UI shows the message banner + per-field
  text, and **does not trim** anything client-side.

## Requirement

Tighten work-item input validation **end to end**:

1. **Trim on write, not in storage**: the server trims `title` and `notes`
   (`String.prototype.trim()`) before validation/storage; the response
   returns the trimmed values. (Behavior change: `"  padded title  "` is now
   stored as `"padded title"`.)
2. **Length limits (server-enforced)**: after trimming, `title` must be
   1–120 chars inclusive; `notes` ≤ 2000 chars. Violations → 400
   `validation_failed` with:
   - `fields.title` = `"title must be 1-120 characters."`
   - `fields.notes` = `"notes must be at most 2000 characters."`
3. **Whitespace-only title is now invalid** (trim makes it empty): error
   `fields.title` = `"title must be 1-120 characters."`
4. **UI**: the item form trims `title`/`notes` before submit, disables the
   submit button when the trimmed title is empty (button stays enabled for
   other invalid inputs so server errors stay observable), and shows a
   client-side hint `aria-describedby` under Title reading
   `"Required. 1-120 characters."` (static hint, not live validation).
5. **Existing seeded data is untouched** (seed titles already satisfy the
   rules; no migration).

## Public examples

- `POST .../items` with `{"title":"  Shipping checklist  "}` → 201 with
  `title:"Shipping checklist"` (and DB row has no surrounding spaces).
- `POST .../items` with `{"title":"   "}` → 400, `fields.title` message as
  above; no row created (verify via fresh connection).
- `PATCH` with `{"title":"x".repeat(121)}` → 400 with the title message;
  `version` unchanged; `{"notes":"y".repeat(2001)}` → 400 notes message.
- UI: submit form with title "  plan  " → created card shows "plan"; with
  empty title the Create button is disabled.

## Boundaries & non-goals

- No unicode/collation rules, no profanity/blacklists, no per-language
  limits, no HTML sanitization (React escapes already).
- Do NOT touch `status`, `dueDate`, or workspace `name` validation.
- No client-side live validation beyond the disabled button + static hint.
- Do not change the error envelope or existing codes.

## Compatibility expectations

- Existing api tests asserting verbatim storage of `"  padded title  "` are
  **expected to be updated** to the new trimmed behavior — update minimally
  and add the new cases; everything else in `npm run check:full` must stay
  green.
- PATCH partial semantics unchanged (absent fields untouched).

## Ownership

- Owns: `shared/domain.ts` (or new `shared/validation.ts`) validation
  helpers + unit tests, `server/api.ts` input handling, `ItemForm.tsx`
  trim/disable/hint, minimal test updates.
- Must not touch: schema DDL, seed data, auth, delete confirm flow.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| Trim on write | api test: create + patch with padded strings → trimmed in response AND in a second-connection DB read |
| Limits | api tests: 120/121 title, 2000/2001 notes boundaries |
| Whitespace title | api test: 400 + exact field message |
| UI behavior | e2e: disabled button on empty title; hint present; padded submit renders trimmed |
| No regression | updated api tests + `npm run check` exit 0 |
