# S03 — Stable cursor pagination on the item list

- Status: DRAFT (not qualified)
- Kind: scored
- Area: pagination
- Conflicts with: S02 (filter param) — this task owns the query-param surface
  on the items list; independent on the baseline.

## Baseline behavior

`GET .../items` returns **all** items in `updated_at DESC, id ASC` order with
no limit. A workspace with 10k items would return 10k items. No cursor, no
`limit`, no page metadata.

## Requirement

Add keyset (cursor) pagination that stays stable under concurrent updates:

1. Params: `limit` (1–100 inclusive; default 20) and `cursor` (opaque).
   Invalid `limit` (non-integer, <1, >100) → 400 `validation_failed` with
   `fields.limit`. Invalid `cursor` → 400 with `fields.cursor` =
   `"cursor is not valid."`.
2. Cursor: base64url of `JSON.stringify([updatedAt, id])` **without padding**
   (`Buffer.from(x).toString("base64url")`). Response envelope changes to
   `{ workspaceId, items, nextCursor }` where `nextCursor` is the cursor of
   the last returned item or `null` when no more items exist.
3. Stability rule: the cursor pins the **(updated_at, id) keyset position**;
   a page fetched with a cursor must never re-serve an item that appeared on
   an earlier page of the same walk, even if other items get updated during
   the walk. Only genuinely new items after the cursor's position may appear
   (documented tolerance).
4. UI: list footer gains **"Load more"** (hidden when `nextCursor === null`);
   clicking appends the next page. The workspace switcher behavior is
   unchanged. A `data-page="n"` attribute on the list marks appended pages
   (n = page index, starting 1) — testable handle for e2e.

## Public examples

- Seeded ws_apollo (8 items): `GET .../items?limit=3` → items
  `[wi_103, wi_106, wi_104]`, `nextCursor` non-null; next page with returned
  cursor + `limit=3` → `[wi_102, wi_107, wi_105]`; final page →
  `[wi_101, wi_108]`, `nextCursor: null`.
- `?limit=0` / `?limit=101` / `?limit=abc` → 400 with `fields.limit`.
- `?cursor=@@@` → 400 with the exact cursor message.
- Walk stability: fetch page 1 (limit 2) → PATCH a **later-page** item (e.g.
  bump wi_101's title) → follow the stored cursor → wi_101 does **not**
  reappear at the walk position it previously occupied later; the walk
  yields each item at most once.

## Boundaries & non-goals

- No OFFSET pagination, no page numbers, no total counts, no reverse
  navigation, no sort parameter (baseline ordering only).
- No infinite-scroll; explicit "Load more" button only.
- Do not change the shape of `WorkItem`.

## Compatibility expectations

- `GET .../items` **without** params: envelope now includes `nextCursor`
  (additive) and defaults to the first 20 items — baseline api tests that
  assumed "all items in one response" must be updated **minimally** (they
  are allowed to request `?limit=100`); everything else stays green.
- Baseline `npm run check:full` green after implementer's minimal updates.

## Ownership

- Owns: cursor codec (pure helper in `shared/` or `server/` with unit tests),
  keyset SQL in `server/api.ts`, envelope change, UI "Load more" +
  `data-page`, updated/new api tests + e2e test (create >20 items via API
  then click through two pages).
- Must not touch: auth, seed manifest, delete/edit semantics.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| Cursor walk | api test: seeded walk with limit 3 → exact page sequences → nextCursor null at end |
| Param validation | api tests: limit/cursor error cases with exact field messages |
| Keyset stability | api test: update during walk → no duplicates/reordering within walk |
| Default limit | api test: no-params returns 20 + nextCursor on the ≥20 workspace |
| UI | e2e: seed >20 via API, "Load more" appends page 2, button hides at end |
