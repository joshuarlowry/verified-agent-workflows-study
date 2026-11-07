# S04 — Transactional JSON import of work items

- Status: DRAFT, revision R1 (not qualified)
- Kind: scored
- Area: import transactionality
- Conflicts with: S05 (export) — the import payload here is its own minimal
  format and deliberately does NOT consume S05's export; both tasks are
  independent on the baseline, never combined (reset-per-task policy in
  `README.md`).

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
   - Array-level rules (HTTP 400, code `validation_failed`, exact
     `fields.items` messages): `items` missing or not an array →
     `"items must be an array."`; empty array →
     `"items must be a non-empty array."`; more than 200 entries →
     `"items must contain at most 200 entries."`.
   - Per-entry validation follows baseline create rules exactly (title
     non-empty string; notes string; status enum; dueDate null or
     `YYYY-MM-DD` shape; unknown per-entry keys ignored; entries must be
     JSON objects; defaults `notes:""`, `status:"open"`, `dueDate:null`).
2. Semantics — single transaction (`better-sqlite3 db.transaction`):
   - **All valid** → every row inserted with **server-generated ids**
     (`wi_…`, like single create), `version:1`, created_by = caller;
     response `201`:
     `{ imported: <n>, items: [<full WorkItem>...] }` in request order.
   - **Any invalid entry** → nothing is inserted; response `422` (code
     `validation_failed`) with `fields.items = "entry <i>: <first problem>"`
     (0-based index) and a fresh-connection read proves zero new rows.
   - **Error priority (exact)**: report the **lowest offending entry
     index**; within an entry, the first failing field in baseline create
     order: `title` → `notes` → `status` → `dueDate`. The embedded message
     is that field's baseline create message (e.g. missing/empty title →
     `"entry 1: title must be a non-empty string."`).
   - Duplicate titles are allowed (no uniqueness rule); duplicate entries
     with identical content are separate rows (nothing deduplicates).
3. UI: an **"Import items"** button (aria-label same) next to "New work
   item" opens a small panel with a labeled textarea **"Items JSON"** and a
   **"Run import"** button. On success: live region announces
   `Imported <n> work items.`, list reloads. On 422/400: the panel shows the
   server message via `role="alert"` and the textarea content is preserved.

## Public examples

- Import 3 valid items → 201, `imported: 3`, items carry server-generated
  `wi_…` ids; a fresh-connection read shows all three rows in the request
  order of the response.
- Import `[{title:"A"},{title:""},{title:"B"}]` → 422 with
  `fields.items = "entry 1: title must be a non-empty string."`; fresh
  read → no "A", no "B" (transaction rolled back).
- Import `[{title:"ok",status:"archived"},{title:""}]` → 422 reporting
  **entry 0** (lowest index wins), not entry 1:
  `fields.items = "entry 0: status must be one of: open, in_progress, done."`.
- Import with `"items": []` → 400 `"items must be a non-empty array."`;
  `"items": "nope"` (or missing) → 400 `"items must be an array."`; 201
  entries → 400 `"items must contain at most 200 entries."`.

## Boundaries & non-goals

- No CSV, no file upload, no mapping/schema negotiation, no partial-import
  mode, no idempotency keys, no update-or-insert (import only creates).
- No dry-run endpoint.
- Does not read or write any export format (S05 is a separate task).
- Disclosed boundaries: entries are never updated by import (no
  upsert-on-duplicate); the 422 status is import-specific (baseline
  validation failures stay 400); array-level vs entry-level errors are
  exactly the 400/422 split above.

## Compatibility expectations

- Baseline single-create endpoint unchanged.
- `npm run check:full` stays green (no baseline test edits).

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
| Exact error priority | api test: lowest entry index reported; field order title→notes→status→dueDate inside an entry |
| Limits | api tests: empty array, non-array, >200 entries — exact `fields.items` messages |
| Server ids | api test: imported rows carry fresh `wi_…` ids not supplied by the client |
| UI | e2e: success announcement + reload; failure alert + preserved input |
