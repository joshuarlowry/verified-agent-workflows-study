# S05 — High-fidelity JSON export

- Status: DRAFT, revision R1 (not qualified)
- Kind: scored
- Area: export fidelity
- Conflicts with: S04 (import) — deliberately independent formats; S03
  (pagination) — export bypasses pagination. Independent on the baseline,
  never combined (reset-per-task policy in `README.md`).

## Baseline behavior

There is no export of any kind. The only ways to read data are the list
endpoint (JSON, camelCase) and raw SQLite.

## Requirement

Add a deterministic, round-trip-faithful export:

1. `GET /api/workspaces/:id/export` (member) → `200` with
   `Content-Type: application/json` and body:
   ```json
   {
     "format": "workboard.export/v1",
     "exportedAt": "<ISO>",
     "workspace": { "id": "…", "name": "…", "createdAt": "…", "updatedAt": "…" },
     "items": [ { "id": "…", "workspaceId": "…", "title": "…", "notes": "…",
                  "status": "…", "dueDate": null, "version": 1,
                  "createdBy": "…", "createdAt": "…", "updatedAt": "…" } ]
   }
   ```
   - **Field order exactly as shown** (insertion order of the JSON object):
     item fields are `id, workspaceId, title, notes, status, dueDate,
     version, createdBy, createdAt, updatedAt` — this includes
     `workspaceId`, so every `work_items` column appears exactly once.
   - `items` ordered `created_at ASC, id ASC` (NOT the list endpoint's
     updated_at ordering) and exported **complete** (no pagination, no
     filters; includes `version` and all columns).
   - `exportedAt` is the only nondeterministic field.
2. Fidelity rules:
   - Every `work_items` column appears exactly once with its wire name
     (`id`, `workspace_id`→`workspaceId`, `title`, `notes`, `status`,
     `due_date`→`dueDate`, `version`, `created_by`→`createdBy`,
     `created_at`→`createdAt`, `updated_at`→`updatedAt`).
   - Values byte-faithful: titles with newlines/quotes/unicode round-trip
     exactly. Equality is asserted **after the snake_case→camelCase mapping
     above**: for every column, `JSON.parse(export).items[i].<camelField>`
     equals the DB row's `<snake_field>` (not literal object equality with
     the raw row).
   - `Content-Disposition: attachment; filename="workspace-<id>-export.json"`.
3. UI: an **"Export JSON"** button (aria-label same) in the workspace
   section triggers a browser download of the current workspace (create an
   object URL from a fetch of the endpoint; the download filename must be
   `<name-with-spaces-dashed>-export.json`, e.g.
   `apollo-launch-export.json` — derived from workspace name, lowercased,
   spaces → dashes). Live region announces `Export ready.`

## Public examples

- Seed ws_apollo → export → `items` ids in `created_at ASC, id ASC` order:
  `wi_101, wi_108, wi_102, wi_107, wi_104, wi_105, wi_103, wi_106`
  (created_at: wi_101 09:10, wi_108 09:20, wi_102 10:00, wi_107 10:15,
  wi_104 10:30, wi_105 10:45, wi_103 11:00, wi_106 11:30 on 2026-11-01).
  The acceptance check may additionally compare export order to
  `SELECT ... ORDER BY created_at ASC, id ASC` programmatically.
- A title `line1\nline2 "quoted" ✓` round-trips byte-exact in the export.
- Non-member (cleo) exporting ws_apollo → 404 `not_found`.

## Boundaries & non-goals

- No CSV/markdown/XML, no import (S04's format is unrelated), no
  selective export, no include-deleted (deleted rows are gone), no
  pretty-printing guarantee (consumers parse JSON; formatting is free).
- No gzip, no streaming (small data).

## Compatibility expectations

- Additive endpoint; no existing response changes.
- `npm run check:full` stays green (no baseline test edits).

## Ownership

- Owns: export endpoint + serializer (pure function + unit tests for order
  and field mapping), UI button + download logic, api tests (shape, order,
  fidelity, membership), e2e test (download event filename + parse).
- Must not touch: list endpoint, schema, auth.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| Shape + field order | api test: `Object.keys` of item/export objects match the contract order (incl. `workspaceId`) |
| Full fidelity | api test: create tricky-content item → export → per-field equality with a fresh-connection DB read after the camelCase mapping |
| Ordering | api test: export order == SQL `created_at ASC, id ASC`; seeded ws_apollo exact sequence above |
| Membership | api test: non-member → 404 envelope |
| UI download | e2e: download event, suggested filename `apollo-launch-export.json`, parses as JSON with format tag |
