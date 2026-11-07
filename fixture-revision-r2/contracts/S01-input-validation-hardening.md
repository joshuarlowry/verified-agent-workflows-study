# S01 — Input validation hardening: trim, limits, field errors

- Status: DRAFT, revision R1 (not qualified)
- Kind: scored
- Area: validation (API + UI)
- Conflicts with: S09 (both touch PATCH semantics — different fields), S08
  (due-date rules — this task must not add date logic). Independent on the
  baseline, never combined (reset-per-task policy in `README.md`).

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
3. **Unified title message**: every title failure — missing at creation,
   empty, whitespace-only (trim makes it empty), non-string, or over 120
   chars — yields the single message `fields.title` =
   `"title must be 1-120 characters."`. The old
   `"title must be a non-empty string."` / `"title is required."` messages
   are replaced by it for work items (workspace `name` validation is
   explicitly NOT touched).
4. **UI**: the item form trims `title`/`notes` before submit, disables the
   submit button when the trimmed title is empty (button stays enabled for
   other invalid inputs, e.g. over-limit notes, so server errors stay
   observable), and shows a client-side hint `aria-describedby` under Title
   reading `"Required. 1-120 characters."` (static hint, not live
   validation).
5. **Existing seeded data is untouched** (seed titles already satisfy the
   rules; no migration).

## Public examples

- `POST .../items` with `{"title":"  Shipping checklist  "}` → 201 with
  `title:"Shipping checklist"` (and DB row has no surrounding spaces).
- `POST .../items` with `{"title":"   "}` → 400, `fields.title` message as
  above; no row created (verify via fresh connection).
- `POST .../items` with `{"title":"x".repeat(121)}` → 400 with the title
  message; `{"title":"t","notes":"y".repeat(2001)}` → 400 notes message;
  boundary values (title 120 chars, notes 2000 chars) → 201/200.
- PATCH `{"title":"x".repeat(121)}` → 400; `version` unchanged.
- UI: submit form with title "  plan  " → created card shows "plan"; with
  an empty (or whitespace-only) title the Create/Save button is disabled
  and the hint is visible.

## Boundaries & non-goals

- No unicode/collation rules, no profanity/blacklists, no per-language
  limits, no HTML sanitization (React escapes already).
- Do NOT touch `status`, `dueDate`, workspace `name` validation, or the
  error envelope/codes (`validation_failed`, message
  `"Invalid work item input."` stay).
- No client-side live validation beyond the disabled button + static hint.
- Disclosed boundary: trimming uses `String.prototype.trim()` exactly (no
  Unicode-aware trimming); length is measured in UTF-16 code units
  (`.length`) after trimming.

## Compatibility expectations — enumerated public test migrations

Under `README.md`'s uniform rule, exactly these baseline test expectations
migrate (behavioral coverage preserved; everything else untouched):

- `tests/api/items.test.ts` — "stores titles verbatim (no trimming in the
  baseline)": expected title becomes `"padded title"` (trimmed); rename the
  test title accordingly and keep the second-connection DB proof if
  present.
- `tests/api/items.test.ts` — "rejects invalid input with per-field
  messages": `fields.title` assertion changes from `toContain("non-empty")`
  to the exact new title message; `fields.status` / `fields.dueDate`
  assertions stay.
- `tests/api/items.test.ts` — "rejects a missing title at creation": stays
  (still 400 + truthy `fields.title`); its message content is covered by
  the new exact-message assertions the implementer adds.
- `tests/unit/domain.test.ts` — "baseline title validation": the
  whitespace-only expectation `isValidTitle("   ")` → the task's validator
  (S01 owns `shared/` validation; the migrated unit test asserts the new
  rule: whitespace-only is invalid, 1–120 inclusive boundaries). The old
  helper/expectation pair is replaced by the task's validator suite.
- `e2e/items.spec.ts` — "submitting an empty title surfaces the baseline
  validation message": **replaced** by the task's e2e checks (disabled
  Create button on empty title + static hint visible) because the submit
  path is disabled for empty titles; the server-side empty/whitespace
  title path is covered by the API tests above, not by clicking a disabled
  button.

All other unit/api/e2e tests stay green untouched.

## Ownership

- Owns: `shared/domain.ts` (or new `shared/validation.ts`) validation
  helpers + unit tests, `server/api.ts` input handling, `ItemForm.tsx`
  trim/disable/hint, the enumerated test migrations above.
- Must not touch: schema DDL, seed data, auth, delete confirm flow.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| Trim on write | api test: create + patch with padded strings → trimmed in response AND in a second-connection DB read |
| Limits | api tests: 120/121 title, 2000/2001 notes boundaries |
| Whitespace title | api test: 400 + exact `title must be 1-120 characters.` message |
| UI behavior | e2e: disabled button on empty title; hint present; padded submit renders trimmed |
| No regression | migrated tests + `npm run check` exit 0 |
