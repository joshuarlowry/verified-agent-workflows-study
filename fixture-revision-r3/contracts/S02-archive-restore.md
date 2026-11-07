# S02 — Archive and restore work items

- Status: DRAFT, revision R1 (not qualified)
- Kind: scored
- Area: archive/restore (full stack)
- Conflicts with: S03 (list surface), S11 (bulk ops). Independent on the
  baseline, never combined (reset-per-task policy in `README.md`).

## Baseline behavior

Deletion is the only removal: hard `DELETE`, 204, row gone. There is no
archived state, no archive column, no filter, no restore. `status` has
exactly three values (`open`, `in_progress`, `done`) and the CHECK constraint
rejects anything else.

## Requirement

Add archive/restore as a **fourth item lifecycle state kept out of
`status`**:

1. Schema: add nullable column `archived_at TEXT` (ISO timestamp) to
   `work_items` via idempotent `ALTER TABLE ... ADD COLUMN` guarded by a
   `PRAGMA table_info` check in `migrate()` (existing DB files must keep
   working; schema_version stays 1 → treat as additive 1.x, document in code).
2. API:
   - `POST /api/items/:id/archive` (member) → sets `archived_at = now`,
     `200` item with `archivedAt`; archiving twice → 409 `conflict` with
     message `"Item is already archived."`.
   - `POST /api/items/:id/restore` (member) → clears `archived_at`, `200`
     item with `archivedAt: null`; restoring a non-archived item → 409
     `conflict` with message `"Item is not archived."`.
   - Archive/restore set **only** `archived_at`: `status`, `version` and
     `updated_at` are untouched by both operations (so list ordering is
     unaffected by archiving; disclosed product decision).
   - List filtering (`GET .../items?filter=…`): archived items are
     **excluded from the default list**; the filter parameter selects the
     view:
     - no param, or `?filter=active` → non-archived only (default)
     - `?filter=archived` → archived only, same ordering
     - `?filter=all` → both, same ordering
     - any other explicit value → 400 `validation_failed` with
       `fields.filter = "filter must be one of: active, archived, all."`
       (same explicit-invalid-parameter policy as C2's `sort`).
   - PATCH/DELETE on an archived item → 409 `conflict`
     (`"Archived items are read-only."`) — except the restore call itself.
   - Wire type gains `archivedAt: string | null`.
3. UI:
   - Row action **"Archive"** (aria-label `Archive <title>`) for non-archived
     items; archived rows render in a separate section/list titled
     **"Archived"** (`aria-label` same) shown only when the workspace has
     archived items, each with **"Restore"** (aria-label
     `Restore <title>`) and read-only rendering (no Edit/Delete buttons).
   - Default "Work items" list must not contain archived rows.
   - Live region announces `"Work item archived."` / `"Work item restored."`

## Public examples

- As ada: archive "Prepare demo script" → `200` with
  `archivedAt:"2026-..."`; `GET .../items` no longer lists it;
  `GET .../items?filter=archived` lists it once.
- Archive twice → `409 {"error":{"code":"conflict","message":"Item is
  already archived."}}`.
- PATCH on it → 409; restore → `200 archivedAt:null`; it reappears in the
  default list.
- e2e: archive seeded "Fix mobile nav overflow" → it leaves "Work items" and
  appears under "Archived"; restore returns it.

## Boundaries & non-goals

- No auto-archive, no scheduled jobs, no bulk archive, no archive
  permissions (any member), no trash bin, no undo beyond Restore.
- Do not reuse `status` values; do not add status values.
- No count badges, no archive reasons/comments.

## Compatibility expectations

- Baseline CRUD on non-archived items unchanged; delete of an archived item
  is blocked (409) — document this interplay in the task notes.
- All baseline tests stay green after adding the column (nullable +
  excluded-by-default keeps old semantics).

## Ownership

- Owns: `server/db.ts` (guarded ALTER), `shared/types.ts` + wire mapping,
  `server/api.ts` (endpoints + filter), UI (row actions, archived section,
  live announcements), new api + e2e tests.
- Must not touch: seed manifest (new column stays NULL), auth, Better Auth
  tables.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| Column migration | api test: open pre-existing baseline DB file (created before change) → migrate succeeds, column exists |
| Archive/restore semantics | api tests: 200 → excluded from default → in archived filter → restore → back; double archive 409 `"Item is already archived."`; restore non-archived 409 `"Item is not archived."` |
| Filter param | api tests: default excludes archived; `?filter=archived` archived only; `?filter=all` both; unknown value → 400 exact `fields.filter` message |
| Read-only archived | api test: PATCH/DELETE archived → 409, DB unchanged |
| Untouched ordering keys | api test: archive/restore leave `version` and `updated_at` unchanged |
| UI sections | e2e: archive moves row to "Archived" section; restore returns it; live announcements |
| Ordering preserved | api test: `?filter=archived` uses `updated_at DESC, id ASC` |
