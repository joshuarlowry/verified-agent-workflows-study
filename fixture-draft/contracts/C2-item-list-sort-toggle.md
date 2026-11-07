# C2 — Item list sort toggle (calibration)

- Status: DRAFT (not qualified)
- Kind: calibration
- Area: API param + UI control
- Conflicts with: S03 (cursor pagination) — S03 defines its own ordering; if
  both were ever combined, the sort param must remain meaningful. Independent
  on the baseline.

## Baseline behavior

`GET /api/workspaces/:id/items` takes no parameters and always returns
`updated_at DESC, id ASC`. The UI has no sort control.

## Requirement

Add a validated, explicit sort parameter and a matching UI toggle:

1. `GET /api/workspaces/:id/items?sort=updated_desc|updated_asc|title_asc`
   — default (no/unknown value → 400 for unknown **explicit** value, default
   = `updated_desc` when absent) ordering:
   - `updated_desc`: `updated_at DESC, id ASC` (baseline order)
   - `updated_asc`: `updated_at ASC, id DESC`
   - `title_asc`: `title ASC, id ASC` (case-insensitive via `COLLATE NOCASE`)
2. The UI gains a `<select aria-label="Sort items">` with options `Newest
   activity`, `Oldest activity`, `Title A–Z`; changing it re-fetches with the
   corresponding `sort` value and the list visibly reorders.
3. Invalid explicit `sort` value → `400 validation_failed` with
   `fields.sort` message; no rows are returned.

## Public examples

- As ada: `GET /api/workspaces/ws_apollo/items?sort=title_asc` → first item
  `Audit analytics events`, last `Write release notes` (NOCASE order).
- As ada: `GET /api/workspaces/ws_apollo/items?sort=updated_asc` → first
  `Archive old assets` (oldest updated), last `Prepare demo script`.
- `?sort=banana` → 400 `{"error":{"code":"validation_failed","fields":
  {"sort":"sort must be one of: updated_desc, updated_asc, title_asc."}}}`.
- UI: choose "Title A–Z" → first card heading becomes "Audit analytics
  events" without a page reload.

## Boundaries & non-goals

- No persistence of the choice (no localStorage/query-param in the URL).
- No filters, no pagination, no changes to item shape.
- `title_desc` / case-sensitive collation / natural sort are out of scope.

## Compatibility expectations

- No-`sort` requests behave exactly as baseline (bit-identical ordering).
- `npm run check:full` stays green.

## Ownership

- Owns: query-param parsing + ordering in `server/api.ts` (may extend the
  list query), `Sort items` select in `src/components/Workboard.tsx`
  (prop-drill or small hook), new unit test for the order-key helper if
  extracted, new api tests + one e2e test.
- Must not touch: seed data, auth, delete/edit flows.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| Three orderings | api tests: exact id sequences for each `sort` on seeded ws_apollo |
| Unknown param | api test: 400 + fields.sort message |
| Default preserved | api test: no-param order identical to baseline |
| UI toggle | e2e: select "Title A–Z" → heading order changes, no reload |
