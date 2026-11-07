# S03 — Stable cursor pagination on the item list

- Status: DRAFT, revision R3 (not qualified)
- Kind: scored
- Area: pagination
- Conflicts with: S02 (filter param) — this task owns the query-param surface
  on the items list; independent on the baseline, never combined
  (reset-per-task policy in `README.md`).

## Baseline behavior

`GET .../items` returns **all** items in `updated_at DESC, id ASC` order with
no limit. A workspace with 10k items would return 10k items. No cursor, no
`limit`, no page metadata.

## Requirement

Add keyset (cursor) pagination with an **explicitly bounded, realizable
consistency model**:

1. Params: `limit` (1–100 inclusive; default 20) and `cursor` (opaque).
   Invalid `limit` (non-integer, <1, >100) → 400 `validation_failed` with
   `fields.limit`. Invalid `cursor` (undecodable, not JSON, or not a
   2-element `[string, string]` array) → 400 with `fields.cursor` =
   `"cursor is not valid."`.
2. Cursor: base64url of `JSON.stringify([updatedAt, id])` **without padding**
   (`Buffer.from(x).toString("base64url")`). Response envelope changes to
   `{ workspaceId, items, nextCursor }` where `nextCursor` is the cursor of
   the last returned item or `null` when no more items exist. A cursor
   decodes to the keyset position `(updated_at, id)`; pages are live keyset
   queries (`updated_at DESC, id ASC`, strictly after the cursor).
3. **Consistency model (the contract — implement and test exactly this):**
   - *Total order.* A page is a strict keyset query over
     (`updated_at` DESC, `id` ASC): the cursor decodes to
     `(updatedAt, id)` and the next page returns only rows strictly after
     that position (`updated_at < cursor.updated_at`, or
     `= cursor.updated_at AND id > cursor.id`). Over an unchanged table
     this serves every item exactly once, ties included (the id tiebreak
     makes the order total).
   - *Live writes and cursor boundary.* A create or PATCH takes key
     `(now, id)`. If its timestamp is strictly newer than the current cursor,
     the row is above the remaining walk: a previously served row cannot
     repeat from that write, and a later-page row is skipped. A new row does
     not appear in remaining pages. If timestamp equals the cursor, an id
     greater than the cursor id sorts after it and can appear or repeat;
     an id at or before the cursor id does not. If timestamp is older than
     the cursor, the write can appear later, including a repeat of a served
     row. The exact strict keyset predicate, not a seen-ID set, governs all
     cases.
   - *Clock and stored keys.* A nondecreasing server clock alone does not
     imply write timestamps are newer than stored timestamps (seed rows can
     be in the future). For a whole walk, no repeats from writes and no new
     rows in later pages follow if **each** mid-walk write timestamp is
     strictly greater than the current cursor timestamp. A sufficient stronger
     condition is every write timestamp strictly greater than the newest
     stored timestamp at walk start; ties must still be excluded. Neither condition is assumed in general. Even a backward clock
     is governed by the same live predicate; no extra stability is promised.
   - *No snapshot / seen-ID guarantees*: concurrent changes, including
     future-key and same-millisecond cases, may skip, repeat or introduce rows
     as described. Acceptance may only assert the conditional guarantees.
   - *Example clock precondition.* For the top-position example below,
     observe the PATCH response `updatedAt` strictly greater than the newest
     pre-PATCH item timestamp, not merely the page cursor. Seed timestamps
     reach `2026-11-04T10:15:00.000Z`; no wall-clock date is assumed.
4. UI: list footer gains **"Load more"** (hidden when `nextCursor === null`);
   clicking appends the next page. The workspace switcher behavior is
   unchanged. A `data-page="n"` attribute on the single list element marks
   the **number of pages loaded so far** (1 after the initial load, +1 per
   appended page; not per-page sections) — testable handle for e2e.

## Public examples

- Seeded ws_apollo (8 items): `GET .../items?limit=3` → items
  `[wi_103, wi_106, wi_104]`, `nextCursor` non-null; next page with returned
  cursor + `limit=3` → `[wi_102, wi_107, wi_105]`; final page →
  `[wi_101, wi_108]`, `nextCursor: null`.
- `?limit=0` / `?limit=101` / `?limit=abc` → 400 with `fields.limit`.
- `?cursor=@@@` → 400 with the exact cursor message.
- Walk stability: on the unchanged seed fetch page 1 with `limit=2`,
  remember the cursor and top timestamp `2026-11-04T10:15:00.000Z`; PATCH
  later-page wi_108. For this example, verify its response `updatedAt` is
  strictly greater than that top timestamp (and hence the cursor); make no
  other writes during the walk. Following the cursor skips wi_108 and serves
  the remaining unchanged rows once; a fresh walk lists wi_108 at the top.
  If the precondition fails, do not claim these outcomes: control the test
  clock or use a known-past dataset, then verify the response again.
- Counterexample: with a nondecreasing clock at `2026-01-01`, below the
  future seed timestamps, a created row can appear later and a previously
  served row PATCHed to that time can reappear. At `2026-11-04T09:30:00.000Z`,
  a PATCH is newer than the limit-2 cursor (09:00) but not the top (10:15),
  so it is skipped in the remaining walk yet is not top in a fresh walk.

## Boundaries & non-goals

- No OFFSET pagination, no page numbers, no total counts, no reverse
  navigation, no sort parameter (baseline ordering only).
- No infinite-scroll; explicit "Load more" button only.
- Do not change the shape of `WorkItem`.
- Explicitly NOT promised (asserting them is out of contract): snapshot
  pages, a seen-ID set, immutable page contents across refetches, behavior
  stability under a backward server clock or timestamps behind the cursor.

## Compatibility expectations

- `GET .../items` **without** params: envelope now includes `nextCursor`
  (additive) and defaults to the first 20 items. **No current baseline api
  test needs migration**: the seeded workspaces hold 8 and 5 items (below
  the default 20), and the existing tests assert order/fields, not the
  envelope key set — `nextCursor` is additive. A task test that creates
  more than 20 items must paginate or request `?limit=100` explicitly.
- Baseline `npm run check:full` green, with no baseline test edits.

## Ownership

- Owns: cursor codec (pure helper in `shared/` or `server/` with unit tests),
  keyset SQL in `server/api.ts`, envelope change, UI "Load more" +
  `data-page`, new api tests + e2e test (create >20 items via API then
  click through two pages).
- Must not touch: auth, seed manifest, delete/edit semantics.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| Cursor walk | api test: seeded walk with limit 3 → exact page sequences → nextCursor null at end |
| Param validation | api tests: limit/cursor error cases with exact field messages |
| Consistency model | api test: update later-page item mid-walk; observe `updatedAt` > newest pre-PATCH timestamp, make no other writes → skipped in remaining walk, top on fresh walk; exercise tie and future-key cases per predicate |
| Default limit | api test: a workspace with exactly 20 items → 20 items + `nextCursor: null`; add a 21st → 20 items + non-null `nextCursor`; following the cursor yields the 21st and nothing repeats |
| UI | e2e: seed >20 via API, "Load more" appends page 2 (`data-page` 2), button hides at end |
