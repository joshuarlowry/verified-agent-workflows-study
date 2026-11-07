# S08 — Due-date semantics: tz-safe calendar handling

- Status: DRAFT, revision R1 (not qualified)
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
   - **Server "today" interface (exact)**: the server derives today once
     per request as `new Date().toISOString().slice(0, 10)`; that day
     string is the only time input. The definition helper lives in
     `shared/` and is **pure** with signature `(dueDate: string | null,
     today: "YYYY-MM-DD") → dueState` — it takes day strings, never
     timestamps. Endpoint tests inject today by exporting the derivation
     (or seeding against a computed today); they never assert volatile
     absolute labels (see testing policy below).
3. **UI labels**: the meta line replaces `Due <date>` with:
   - `Overdue — due 2026-11-05` (pill class `pill-overdue`, red text)
   - `Due today` (`pill-due-today`)
   - `Due in 1 day (2026-11-08)` (`pill-due-soon`; singular for N = 1)
   - `Due in 3 days (2026-11-10)` (`pill-due-soon`; plural for 2 ≤ N ≤ 7)
   - `Due 2026-12-01` (`later` — plain, no pill class)
   - `No due date` unchanged.
   Exact strings above are the contract (singular `1 day` / plural
   `<N> days` is part of the grammar).
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
- **Testing policy (no volatile real-time examples)**: api tests compute
  expected states from seeded/created dates with the same pure helper
  injected with a today string (e.g. `"2026-11-07"`), rather than
  asserting absolute labels tied to the wall clock. e2e tests are
  time-robust: they assert (a) the permanently-past seeded item wi_102
  (due 2026-11-05) always renders `Overdue — due 2026-11-05`, and (b)
  relative labels via items the test creates at run time from real today
  (dueDate = today−1 → `Overdue — due <d>`; today+1 → `Due in 1 day (<d>)`;
  today+30 → `Due <d>` plain), where `<d>` are the concrete dates the test
  computed. If a fixed fake clock is used instead (`page.clock`), the
  server and page clock must be pinned to the same instant; either
  approach is acceptable, neither may depend on the date the fixture was
  authored.

## Boundaries & non-goals

- No due-date editing UI changes beyond the existing field; no
  reminders/notifications; no date sorting; no "this week" filters; no
  local-timezone display conversion (server UTC day only, documented).
- Do not change `version`, PATCH rules, or other fields' validation (S01).
- Disclosed boundary: `dueState` is computed per request from the server
  clock; clients do not recompute it (the label grammar above is the UI's
  rendering of the server-provided state + dueDate).

## Compatibility expectations

- `dueDate` remains a nullable `YYYY-MM-DD` string; wire changes are additive
  (`dueState`).
- Baseline api tests that assert due-date **shape** validation
  (`isValidDueDateFormat`, `2026-02-30` accepted as shape-valid) — the unit
  test asserting `isValidDueDateFormat("2026-02-30") === true` still passes
  because the *shape* helper is unchanged; real-calendar rejection is new
  server-level validation added alongside it. No baseline test edits.
- `npm run check:full` green.

## Ownership

- Owns: `shared/dates.ts` (pure parse/compare/label helpers + unit tests),
  `server/api.ts` validation + `dueState` computation, `StatusPill`/meta
  line rendering + CSS classes, api + e2e tests (relative-semantics strategy
  above).
- Must not touch: seed manifest values, auth, other validation.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| Real-date validation | api tests: `2026-02-30` → 400 exact message; `2024-02-29` → 201; `1999-12-31` → 400 same message |
| dueState definition | unit tests: table of (dueDate, today) → state incl. derived UTC-flip day strings and leap year |
| Wire field | api test: list items carry `dueState` consistent with the helper (injected today, no volatile absolutes) |
| UI labels | e2e: overdue seeded item exact `Overdue — due 2026-11-05`; relative probes today−1/today+1/today+30 → exact labels |
| Storage unchanged | api test: stored due_date string identical after validation |
| Label grammar | unit test: N=1 singular vs N≥2 plural exact strings |
