# S03 — Stable cursor pagination on the item list

- Status: DRAFT, revision R1 (not qualified)
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
   - *No repeats within a walk.* Following `nextCursor` yields each item at
     most once, **provided `updated_at` values never decrease**. This holds
     because the baseline can only move a key forward: PATCH sets
     `updated_at` to the current server clock, and create only adds items
     with current-clock timestamps. A server wall-clock step *backwards*
     could move a key backwards and is outside the model (documented
     limitation, not tested).
   - *Live-keyset tolerance (disclosed).* Pages are not snapshots. Between
     page fetches: an item whose key moves **before** the cursor (PATCH
     bumps its `updated_at` above the cursor position) leaves the remaining
     walk and is **skipped** — it reappears only on a fresh walk from page
     1. An item created during the walk has a key newer than the walk's
     starting position and does **not** appear in later pages of that walk.
     No page shows an item twice, and no reordering occurs within a walk.
   - *No snapshot / seen-ID guarantees are promised*: the model is keyset +
     the two rules above, nothing more. Acceptance checks may only assert
     this model.
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
  the cursor; PATCH a **later-page** item (e.g. bump wi_108's title — it
  moves to a key above the cursor); follow the cursor through the rest of
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
| Consistency model | api test: update a later-page item mid-walk → walk still yields each item at most once, skipped item returns on a fresh walk |
| Default limit | api test: no-params returns 20 + nextCursor on a ≥20-item workspace |
| UI | e2e: seed >20 via API, "Load more" appends page 2 (`data-page` 2), button hides at end |
