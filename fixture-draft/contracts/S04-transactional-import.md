# S04 — Transactional JSON import of work items

- Status: DRAFT (not qualified)
- Kind: scored
- Area: import transactionality
- Conflicts with: S05 (export) — the import payload here is its own minimal
  format and deliberately does NOT consume S05's export; both tasks are
  independent on the baseline.

## Baseline behavior

Items are created one at a time (`POST .../items`); each insert is its own
transaction; a failure mid-way leaves earlier rows committed (there is no
bulk endpoint at all).

## Requirement

Add an all-or-nothing import endpoint:

1. `POST /api/workspaces/:id/items/import` (member), body:
   ```json
   { "items": [ { "title": "…", "notes": "…", "status": "open", "dueDate": "2026-11-20" }, … ] }
   ```
   - `items` must be a non-empty array, ≤ 200 entries.
   - Per-entry fields follow baseline create rules **plus** the exact same
     validation as baseline create (title non-empty; status enum; dueDate
     null/`YYYY-MM-DD` shape; notes string). Unknown per-entry keys are
     ignored.
2. Semantics — single transaction (`better-sqlite3 db.transaction`):
   - **All valid** → every row inserted with server ids, `version:1`,
     created_by = caller; response `201`:
     `{ imported: <n>, items: [<full WorkItem>...] }` in request order.
   - **Any invalid entry** → nothing is inserted; response `422` (code
     `validation_failed`) with
     `fields.items = "entry <i>: <first problem>"` (0-based index) — e.g.
     `"entry 2: title must be a non-empty string."` — and a fresh-connection
     read proves zero new rows.
   - Duplicate titles are allowed (no uniqueness rule).
3. UI: an **"Import items"** button (aria-label same) next to "New work
   item" opens a small panel with a labeled textarea **"Items JSON"** and a
   **"Run import"** button. On success: live region announces
   `Imported <n> work items.`, list reloads. On 422/400: the panel shows the
   server message via `role="alert"` and the textarea content is preserved.

## Public examples

- Import 3 valid items → 201, `imported: 3`, list (fresh connection) shows
  all three with pinned ids; an interrupted… (no crash simulation needed).
- Import `[{title:"A"},{title:""},{title:"B"}]` → 422 with
  `fields.items = "entry 1: title must be a non-empty string."`; fresh
  read → no "A", no "B" (transaction rolled back).
- Import with `"items": []` → 400 `validation_failed`
  (`"items must be a non-empty array."`); 201 entries → 400 with limit
  message.

## Boundaries & non-goals

- No CSV, no file upload, no mapping/schema negotiation, no partial-import
  mode, no idempotency keys, no update-or-insert (import only creates).
- No dry-run endpoint.
- Does not read or write any export format (S05 is a separate task).

## Compatibility expectations

- Baseline single-create endpoint unchanged.
- `npm run check:full` stays green.

## Ownership

- Owns: `server/api.ts` import endpoint (transaction), wire types, UI panel
  in `Workboard.tsx` (+ minimal CSS), api tests (success/rollback/limits) +
  e2e test (import 2 valid items → both visible; invalid import → alert +
  textarea preserved).
- Must not touch: auth, schema DDL, existing create/update/delete.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| All-or-nothing | api test: valid batch → 201 + rows via second connection; invalid entry → 422 + zero rows |
| Exact error index | api test: entry index in message |
| Limits | api tests: empty array, >200 entries, wrong types |
| UI | e2e: success announcement + reload; failure alert + preserved input |
