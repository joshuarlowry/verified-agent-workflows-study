# S08 — Due-date semantics: tz-safe calendar handling

- Status: DRAFT (not qualified)
- Kind: scored
- Area: calendar dates
- Conflicts with: S01 (this task must NOT change title/notes validation),
  S14 (summary must not redefine overdue — S08 owns the definition).

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
   `fields.dueDate = "dueDate must be a real calendar date (YYYY-MM-DD)."`;
   `2024-02-29` valid leap day). Years restricted to 2000–2099. Stored and
   returned unchanged (still a plain string).
2. **Server-computed status (member of list + single responses)**: each item
   gains additive read-only fields:
   - `dueState`: `"none" | "overdue" | "due_today" | "due_soon" | "later"`
     where — relative to **UTC "today"** (the server's date, defined as
     `new Date().toISOString().slice(0,10)`):
     `none` (no dueDate), `overdue` (< today), `due_today` (== today),
     `due_soon` (within the next 7 calendar days inclusive of tomorrow,
     i.e. today < due ≤ today+7), `later` (> today+7).
   - The definition helper lives in `shared/` and is pure (input: dueDate
     string, today string → state).
3. **UI labels**: the meta line replaces `Due <date>` with:
   - `Overdue — due 2026-11-05` (pill class `pill-overdue`, red text)
   - `Due today` (`pill-due-today`)
   - `Due in 3 days (2026-11-10)` (`pill-due-soon`)
   - `Due 2026-12-01` (`later` — plain, no pill class)
   - `No due date` unchanged.
   Exact strings above are the contract.
4. **Date safety guarantees**: the compute helper must be unit-tested for
   the UTC boundary (e.g. `dueDate=2026-11-07`, `today=2026-11-07T23:59Z`
   vs `2026-11-08T00:01Z` flip) and leap years. No `new Date("YYYY-MM-DD")`
   local parsing (documented forbidden pattern).

## Public examples

- Server "today" = 2026-11-07 (test pins today by injecting it into the
  helper; api tests inject via exported helper — for endpoint tests, seed
  dates are fixed and the test computes expected states with the same pure
  helper rather than asserting volatile absolute labels).
- `POST .../items {"dueDate":"2026-02-30"}` → 400 with the exact real-date
  message; `"2024-02-29"` → 201.
- PATCH `{"dueDate":null}` clears → `dueState:"none"`.
- UI: wi_102 (due 2026-11-05, seed) renders overdue styling whenever today
  > 2026-11-05; wi_101 (2026-11-12) renders `Due in N days (2026-11-12)`
  when N ≤ 7.

## Boundaries & non-goals

- No due-date editing UI changes beyond existing field; no reminders/notifications; no date sorting; no "this week" filters; no local-timezone
  display conversion (server UTC day only, documented).
- Do not change `version`, PATCH rules, or other fields' validation (S01).

## Compatibility expectations

- `dueDate` remains a nullable `YYYY-MM-DD` string; wire changes are additive
  (`dueState`).
- Baseline api tests asserting `2026-02-30`-shape acceptance… (there are
  none asserting it — only shape tests via `isValidDueDateFormat`) stay
  green; the implementer adds real-date tests.
- `npm run check:full` green.

## Ownership

- Owns: `shared/dates.ts` (pure parse/compare/label helpers + unit tests),
  `server/api.ts` validation + `dueState` computation, `StatusPill`/meta
  line rendering + CSS classes, api + e2e tests (e2e asserts relative
  semantics via a fixed fake-time context if needed — `page.clock` or
  deterministic assertions on seeded far-future/past dates).
- Must not touch: seed manifest values, auth, other validation.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| Real-date validation | api tests: 2026-02-30 → 400 exact message; 2024-02-29 → 201; 1999-12-31 → 400 |
| dueState definition | unit tests: table of (dueDate, today) → state incl. UTC flip and leap year |
| Wire field | api test: list items carry dueState consistent with helper |
| UI labels | e2e: overdue item shows exact `Overdue — due 2026-11-05`; far-future shows `Due 2026-12-01` |
| Storage unchanged | api test: stored due_date string identical after validation |
