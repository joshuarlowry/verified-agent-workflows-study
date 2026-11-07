# S08 — Due-date semantics: tz-safe calendar handling

- Status: DRAFT, revision R2 (not qualified)
- Kind: scored
- Area: calendar dates
- Conflicts with: S01 (this task must NOT change title/notes validation),
  S14 (summary must not redefine overdue — S08 owns the definition).
  Independent on the baseline, never combined (reset-per-task policy in
  `README.md`).

## Baseline behavior (explicit)

`dueDate` is an opaque `YYYY-MM-DD` string, shape-validated only
(`2026-02-30` is accepted). The UI displays the raw string
(`Due 2026-11-12` / `No due date`). Nothing computes over dates; there are no
overdue states, no relative labels, no date filters.

## Requirement

Introduce real calendar-date semantics, computed **timezone-safely** (all
date math on `YYYY-MM-DD` strings or UTC; never local-time Date arithmetic):

1. **Real-calendar validation (server)**: `dueDate` must parse as a real
   calendar date (e.g. `2026-02-30` → 400
   `fields.dueDate = "dueDate must be a real calendar date (YYYY-MM-DD)."`
   and `"1999-12-31"` → 400 with the same message, year outside
   2000–2099; `2024-02-29` is a valid leap day). Years restricted to
   2000–2099. Stored and returned unchanged (still a plain string).
2. **Server-computed status (additive read-only field)**: each item in list
   and item responses gains:
   - `dueState`: `"none" | "overdue" | "due_today" | "due_soon" | "later"`
     where — relative to the server's UTC "today" — `none` (no dueDate),
     `overdue` (due < today), `due_today` (due == today), `due_soon` (today
     < due ≤ today+7, i.e. the next 7 calendar days including tomorrow),
     `later` (due > today+7).
   - **Server→client time interface (exact)**: the server derives today
     once per request as `new Date().toISOString().slice(0, 10)` (or the
     pinned test override below); that day string is the only time input.
     The item-list response envelope gains one additive read-only field
     `today: "YYYY-MM-DD"` (the server's day string for that request) next
     to `workspaceId`/`items`, and each item gains `dueState`. The UI
     renders the due meta line from `(dueDate, envelope today)` through the
     shared pure helper — it never reads a clock for due labels. A
     per-item `today` is deliberately NOT added; single-item responses
     carry `dueState` (wire contract) but the UI renders labels from list
     data only (baseline mutations reload the list, so the meta line
     always renders from a fresh envelope). The definition helper lives in
     `shared/` and is **pure** with signature `(dueDate: string | null,
     today: "YYYY-MM-DD") → dueState` — it takes day strings, never
     timestamps.
   - **Test clock override (exact, test-only)**: when the environment
     variable `WORKBOARD_FAKE_TODAY` is set to a real calendar date within
     2000–2099, the server uses that day string as today for `dueState`
     and for the envelope `today` field — nothing else changes
     (`created_at`/`updated_at` keep the real clock). An invalid value
     (not a real `YYYY-MM-DD`, outside 2000–2099) makes the server
     **fail fast at startup** (nonzero exit / build error), never a
     silently ignored override. Without the variable, behavior is
     identical to wall-clock today.
3. **UI labels**: the meta line replaces `Due <date>` with:
   - `Overdue — due 2026-11-05` (pill class `pill-overdue`, red text)
   - `Due today` (`pill-due-today`)
   - `Due in 1 day (2026-11-08)` (`pill-due-soon`; singular for N = 1)
   - `Due in 3 days (2026-11-10)` (`pill-due-soon`; plural for 2 ≤ N ≤ 7)
   - `Due 2026-12-01` (`later` — plain, no pill class)
   - `No due date` unchanged.
   Exact strings above are the contract (singular `1 day` / plural
   `<N> days` is part of the grammar). For `due_soon`, N is the
   calendar-day difference between `dueDate` and the envelope `today`
   (both from the same response) — the UI derives N from those two values,
   never from a clock.
4. **Date safety guarantees**: the compute helper must be unit-tested for
   the UTC boundary and leap years. The UTC-flip test derives the two
   **day strings** from the two timestamps first — server-today for
   `2026-11-07T23:59:59Z` is `"2026-11-07"` and for `2026-11-08T00:00:01Z`
   is `"2026-11-08"` (derivation: `new Date(ts).toISOString().slice(0,10)`)
   — then asserts the helper's outputs for each. No
   `new Date("YYYY-MM-DD")` local parsing (documented forbidden pattern).

## Public examples

- `POST .../items {"title":"Calendar probe","dueDate":"2026-02-30"}` → 400
  with the exact real-date message; `{"title":"Leap day","dueDate":
  "2024-02-29"}` → 201.
- PATCH `{"dueDate":null}` clears → `dueState:"none"`.
- **Testing policy (pinned clocks — no volatile real-time examples)**: the
  e2e run pins the server day via the override above
  (`WORKBOARD_FAKE_TODAY: "2026-11-07"` in the e2e webServer env, the one
  enumerated config exception below); every e2e expectation is then exact
  and stable regardless of the wall clock:
  - seeded wi_102 (due 2026-11-05) → `Overdue — due 2026-11-05` (pill
    `pill-overdue`). This is deterministic **because of the pin** —
    2026-11-05 is not "permanently past" (on a real date on/before it the
    item would be future/today), so no assertion may rely on the wall
    clock;
  - seeded wi_101 (due 2026-11-12) → `Due in 5 days (2026-11-12)` — this
    is the migrated baseline assertion;
  - seeded wi_107 (2026-11-20) and wi_105 (2026-12-01) → plain
    `Due <date>` (later, beyond pinned today+7 = 2026-11-14);
  - runtime-created probes close the remaining grammar/boundary gaps
    under the same pin: due 2026-11-07 → `Due today` (`pill-due-today`);
    2026-11-08 → `Due in 1 day (2026-11-08)` (singular); 2026-11-09 →
    `Due in 2 days (2026-11-09)`; 2026-11-14 → `Due in 7 days
    (2026-11-14)` (due_soon upper boundary, N = 7); 2026-11-15 →
    `Due 2026-11-15` plain (later lower boundary, N = 8).
  api tests pin the same override for their app instance (set
  `WORKBOARD_FAKE_TODAY` before building the test app, clear it
  afterwards) and assert exact `dueState` values against pinned dates.
  Unit tests inject day strings directly — no clock at all. No test
  anywhere asserts a label or state computed from the wall clock.

## Boundaries & non-goals

- No due-date editing UI changes beyond the existing field; no
  reminders/notifications; no date sorting; no "this week" filters; no
  local-timezone display conversion (server UTC day only, documented).
- Do not change `version`, PATCH rules, or other fields' validation (S01).
- Disclosed boundary: `dueState` is computed per request from the server
  day (wall clock, or `WORKBOARD_FAKE_TODAY` when pinned); clients never
  read a clock for due labels — the UI's meta line is a pure rendering of
  `(dueDate, envelope today)` (the exact interface above; no other fields
  are added, and a per-item `today` is explicitly not part of this task).

## Compatibility expectations

- `dueDate` remains a nullable `YYYY-MM-DD` string; wire changes are
  additive and exactly the two specified above (per-item `dueState`,
  envelope `today`) — no others.
- Baseline api tests that assert due-date **shape** validation
  (`isValidDueDateFormat`, `2026-02-30` accepted as shape-valid) — the unit
  test asserting `isValidDueDateFormat("2026-02-30") === true` still passes
  because the *shape* helper is unchanged; real-calendar rejection is new
  server-level validation added alongside it.
- **Enumerated baseline test migrations (exhaustive)** — under
  `README.md`'s uniform rule, exactly these baseline expectations are
  affected, all evaluated under the pinned e2e server day `2026-11-07`:
  - `e2e/items.spec.ts` ("lists seeded items…") — the wi_101 "Draft launch
    checklist" due-date assertion `"Due 2026-11-12"` becomes
    `"Due in 5 days (2026-11-12)"` (due_soon, N = 5 from 2026-11-07). Its
    status/heading assertions stay.
  - `e2e/items.spec.ts` ("creating an item persists…") — the created
    card's `"Due 2026-11-25"` assertion stays **exactly as is** (under the
    pin, 2026-11-25 is beyond today+7 → later → plain `Due 2026-11-25`);
    recorded here to show it was checked against the pinned day, not
    changed.
  - No other baseline unit/api/e2e test asserts a due-date rendering; the
    baseline has no other real-time-dependent e2e assertion (created
    items' due dates are chosen by the tests themselves), so the pinned
    day changes no other baseline result.
- **Enumerated configuration exception (exact)**: the e2e run pins the
  server day by adding exactly one webServer env line to
  `baseline/playwright.config.ts` — `WORKBOARD_FAKE_TODAY: "2026-11-07"` —
  so every e2e test (baseline and task) runs against that server day. This
  is the only permitted configuration change; no other env, option, or
  baseline file is touched.
- `npm run check:full` green (with the single migrated assertion above).

## Ownership

- Owns: `shared/dates.ts` (pure parse/compare/label helpers + unit tests),
  `server/api.ts` validation + `dueState` computation + the
  `WORKBOARD_FAKE_TODAY` override, the envelope `today` field,
  `StatusPill`/meta line rendering + CSS classes, the single enumerated
  webServer env line in `baseline/playwright.config.ts`, api + e2e tests
  (pinned-clock strategy above).
- Must not touch: seed manifest values, auth, other validation, any other
  e2e/server configuration.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| Real-date validation | api tests: `2026-02-30` → 400 exact message; `2024-02-29` → 201; `1999-12-31` → 400 same message |
| dueState definition | unit tests: table of (dueDate, today) → state incl. derived UTC-flip day strings, leap year, and the 2000-01-01/2099-12-31 valid vs 1999-12-31/2100-01-01 invalid boundaries |
| Wire fields | api test (pinned `WORKBOARD_FAKE_TODAY`): list items carry `dueState` consistent with the helper and the envelope carries the pinned `today`; single-item responses carry `dueState` |
| Clock override | api test: an invalid `WORKBOARD_FAKE_TODAY` value fails the app build; a valid value yields the exact pinned `today` in responses |
| UI labels | e2e (pinned server day 2026-11-07): exact labels for wi_102/wi_101/wi_107 and the created boundary probes (Due today, N=1, N=2, N=7 due_soon, N=8 later) |
| Storage unchanged | api test: stored due_date string identical after validation |
| Label grammar | unit test: N=1 singular vs N≥2 plural exact strings; boundary N=7 due_soon vs N=8 later |
