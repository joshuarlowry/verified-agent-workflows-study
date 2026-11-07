# S03 — Stable cursor pagination on the item list

- Status: DRAFT, revision R2 (not qualified)
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
   - *No repeats within a walk.* With a **nondecreasing server clock**, an
     item already served cannot be served again in the same walk — every
     write during a walk takes the key `(now, id)` with `now` at-or-above
     the walk's newest key, so a served item moves out of the remaining
     walk (skip) rather than re-entering it — **except** in the disclosed
     same-millisecond tie case below.
   - *Disclosed same-millisecond tie exception (exact).* A two-field keyset
     has no time resolution finer than 1 ms. A write (PATCH bump or
     create) whose `updated_at` equals the walk cursor's `updated_at` with
     a lexicographically **greater** `id` lands strictly after the cursor
     and CAN appear on a later page of the same walk (created items) or
     reappear (re-served items). Writes in the same millisecond with a
     smaller `id`, and all strictly newer writes, stay out of the remaining
     walk. Ordinary operation (distinct-millisecond writes) and every
     seeded/example walk satisfy the strict guarantee; acceptance may not
     assert the strict form across a same-millisecond tie with a greater id.
   - *Live-keyset skip tolerance (disclosed).* Pages are not snapshots. An
     item PATCHed mid-walk takes the key `(now, id)`; when `now` is
     strictly newer than the cursor's timestamp (the ordinary case) it
     moves above the remaining walk and is **skipped** — it reappears only
     on a fresh walk from page 1.
   - *New items during a walk.* A create during the walk has key
     `(now, id)`; when `now` is strictly newer than the cursor's timestamp
     it does **not** appear in later pages of that walk. The
     same-millisecond tie case above is the only way a mid-walk create can
     surface in a later page.
   - *No snapshot / seen-ID guarantees are promised*: the model is keyset +
     the rules above, nothing more. Acceptance checks may only assert
     this model.
   - *Clock requirement for mutation examples (disclosed).* The
     walk-stability example (a PATCH moves an item above the cursor)
     requires the server clock to be strictly newer than the newest seed
     timestamp (`2026-11-04T10:15:00.000Z`). Tests must **observe** this
     precondition, not assume it: the PATCH response's `updatedAt` must be
     strictly greater than the walk cursor's `updatedAt`, and the example's
     assertions are valid only then (the seed is dated 2026-11-01..04 and
     the reference environment's clock is 2026-11-07+, so ordinary runs
     satisfy it). A server clock stepping *backwards* mid-walk is outside
     the model (documented limitation, not tested).
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
- Walk stability (the model's test): fetch page 1 with `limit=2`, remember
  the cursor; PATCH a **later-page** item (e.g. bump wi_108's title) and
  check the precondition from the PATCH response — its `updatedAt` must be
  strictly greater than the cursor's (server clock newer than the seed,
  see the clock requirement above); follow the cursor through the rest of
  the walk → the walk still yields each remaining item at most once and
  wi_108 does not reappear mid-walk; a fresh walk from page 1 lists wi_108
  at its new (top) position.

## Boundaries & non-goals

- No OFFSET pagination, no page numbers, no total counts, no reverse
  navigation, no sort parameter (baseline ordering only).
- No infinite-scroll; explicit "Load more" button only.
- Do not change the shape of `WorkItem`.
- Explicitly NOT promised (asserting them is out of contract): snapshot
  pages, a seen-ID set, immutable page contents across refetches, behavior
  under a backward server clock.

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
| Consistency model | api test: update a later-page item mid-walk (precondition `updatedAt` > cursor observed) → walk still yields each item at most once, skipped item returns on a fresh walk |
| Default limit | api test: a workspace with exactly 20 items → 20 items + `nextCursor: null`; add a 21st → 20 items + non-null `nextCursor`; following the cursor yields the 21st and nothing repeats |
| UI | e2e: seed >20 via API, "Load more" appends page 2 (`data-page` 2), button hides at end |
