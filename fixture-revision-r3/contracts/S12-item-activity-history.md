# S12 — Item activity history (who changed what, when)

- Status: DRAFT, revision R1 (not qualified)
- Kind: scored
- Area: audit/persistence
- Conflicts with: S09 (may record version — read-only), S11 (bulk updates
  are out of scope here; single-item changes only). Independent on the
  baseline, never combined (reset-per-task policy in `README.md`).

## Baseline behavior

No history exists: updates overwrite in place; only `version` and
`updated_at` hint that something changed, but not what or who. Deleted items
leave no trace.

## Requirement

Record and expose per-item change history for **PATCH updates only**
(create and delete are NOT logged). The recorded fields are exactly
`title`, `notes`, `status`, `dueDate` — all four are in scope (the task
covers field-value changes of any of them, not only status/title):

1. Schema: additive table (idempotent DDL in `migrate()`):
   ```sql
   CREATE TABLE IF NOT EXISTS work_item_events (
     id         TEXT PRIMARY KEY,
     item_id    TEXT NOT NULL REFERENCES work_items(id) ON DELETE CASCADE,
     actor_id   TEXT NOT NULL,             -- Better Auth user.id
     kind       TEXT NOT NULL CHECK (kind IN ('update')),
     changes    TEXT NOT NULL,             -- JSON array of {field, from, to}
     created_at TEXT NOT NULL
   );
   CREATE INDEX IF NOT EXISTS idx_work_item_events_item
     ON work_item_events(item_id, created_at DESC);
   ```
2. Recording rule: a successful PATCH writes **one event** whose `changes`
   lists only the fields that actually changed, in the fixed order
   `title, notes, status, dueDate` (`from`/`to` = prior/new values;
   `dueDate` null-safe, `from`/`to` use `null` for "no date"). A PATCH
   that changes nothing observable (same values) records **no event** but
   still bumps version (baseline PATCH semantics preserved).
3. **Atomicity (exact)**: the item UPDATE and its event INSERT commit in
   the **same transaction** (`better-sqlite3 db.transaction`) — a PATCH is
   all-or-nothing including its event; a crash between them is impossible
   from the API surface.
4. API: `GET /api/items/:id/events` (member) →
   `200 { itemId, events: [{ id, actorId, actorEmail, kind:"update",
   changes:[…], createdAt }] }`, newest first, `created_at DESC, id ASC`
   tiebreak. `?limit` is a cap of 1..50 (default 20); a present-but-invalid
   `limit` (non-integer, <1, >50) → 400 `validation_failed` with
   `fields.limit = "limit must be an integer between 1 and 50."`;
   no pagination/cursor.
4. UI: item card gains **"History"** (aria-label `History <title>`) toggle;
   expanded section (inline, `aria-label "Activity history <title>"`)
   fetches and lists entries as `<actorEmail> changed <field>` lines with
   the changed fields summarized (e.g. `status: open → done`), newest
   first; `aria-expanded` on the toggle. Empty history (never updated) shows
   `No changes recorded yet.`

## Public examples

- PATCH wi_101 title+status by bruno → one event, changes =
  `[{"field":"title","from":"Draft launch checklist","to":"…"},{"field":"status","from":"open","to":"…"}]`,
  actorEmail = bruno.
- Same-values PATCH → 200, version+1, then `GET events` → no new event.
- cleo (non-member) → 404. Unknown id → 404.
- UI: after two edits, history shows 2 lines newest first with the
  `field: from → to` summary.

## Boundaries & non-goals

- No create/delete events, no archive interplay, no event edit/delete, no
  actor display names (email only), no full-text search, no cursor.
- Does not retroactively log baseline-era changes (history starts empty).
- Disclosed boundaries: events record PATCH changes to exactly the four
  fields above (title/notes/status/dueDate); the PATCH+event pair is
  transactional; invalid `?limit` values use the exact 400 message above
  (absent `?limit` = default 20, never an error).

## Compatibility expectations

- Existing PATCH responses/shapes unchanged (events are a side table).
- `npm run check:full` green (no baseline test edits).

## Ownership

- Owns: `server/db.ts` DDL, event recorder (pure diff helper in `shared/` +
  unit tests), events endpoint, UI toggle + rendering, api + e2e tests.
- Must not touch: seed manifest (no events seeded), auth, delete semantics.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| Event written | api test: multi-field PATCH → exactly one event with exact changed-field list (fixed field order) + actor |
| No-op PATCH | api test: same-values PATCH → version+1, zero new events |
| Atomicity | api test: PATCH + event visible together via second connection; no event without the corresponding update |
| Order + cap | api tests: newest-first ordering; ?limit bounds + default; invalid limit → 400 exact message |
| Membership | api test: non-member → 404 |
| UI | e2e: toggle → expanded list lines match `field: from → to`; empty state text for fresh item |
