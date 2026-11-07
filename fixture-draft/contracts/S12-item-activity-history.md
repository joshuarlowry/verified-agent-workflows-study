# S12 — Item activity history (who changed what, when)

- Status: DRAFT (not qualified)
- Kind: scored
- Area: audit/persistence
- Conflicts with: S09 (may record version — read-only), S11 (bulk updates
  are out of scope here; single-item changes only). Independent on the
  baseline.

## Baseline behavior

No history exists: updates overwrite in place; only `version` and
`updated_at` hint that something changed, but not what or who. Deleted items
leave no trace.

## Requirement

Record and expose per-item change history for **updates and status/title
edits only** (create and delete are NOT logged):

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
   lists only the fields that actually changed (title, notes, status,
   dueDate; `from`/`to` = prior/new values, `dueDate` null-safe). A PATCH
   that changes nothing observable (same values) records **no event** but
   still bumps version (baseline PATCH semantics preserved).
3. API: `GET /api/items/:id/events` (member) →
   `200 { itemId, events: [{ id, actorId, actorEmail, kind:"update",
   changes:[…], createdAt }] }`, newest first, `created_at DESC, id ASC`
   tiebreak. `?limit=1..50` (default 20) for cap; no pagination/cursor.
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

## Compatibility expectations

- Existing PATCH responses/shapes unchanged (events are a side table).
- `npm run check:full` green.

## Ownership

- Owns: `server/db.ts` DDL, event recorder (pure diff helper in `shared/` +
  unit tests), events endpoint, UI toggle + rendering, api + e2e tests.
- Must not touch: seed manifest (no events seeded), auth, delete semantics.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| Event written | api test: multi-field PATCH → exactly one event with exact changed-field list + actor |
| No-op PATCH | api test: same-values PATCH → version+1, zero new events |
| Order + cap | api tests: newest-first ordering; ?limit bounds + default |
| Membership | api test: non-member → 404 |
| UI | e2e: toggle → expanded list lines match `field: from → to`; empty state text for fresh item |
