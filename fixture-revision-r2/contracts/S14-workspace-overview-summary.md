# S14 — Workspace overview summary (aggregate panel)

- Status: DRAFT (not qualified)
- Kind: scored
- Area: aggregation
- Conflicts with: C1 (counts — same response surface; C1 is calibration, if
  both were combined the fields coexist), S08 (must NOT redefine overdue —
  this task has no date logic). Independent on the baseline.

## Baseline behavior

No aggregate endpoint or overview UI. Clients would have to fetch all items
and count client-side.

## Requirement

Add a per-workspace aggregate endpoint and a compact overview panel:

1. `GET /api/workspaces/:id/summary` (member) →
   `200 { workspaceId, totalItems, byStatus: { open, in_progress, done },
   lastActivityAt: string | null }` where:
   - `totalItems` = all items in the workspace,
   - `byStatus.*` = counts per status (all three keys always present,
     integers),
   - `lastActivityAt` = max(`updated_at`) across items or `null` when the
     workspace has no items.
   Computed in SQL (COUNT/GROUP BY + MAX), no full-item fetch in JS.
2. UI: a collapsible **"Overview"** section above the list (button
   `aria-expanded`, default collapsed) containing, when expanded, a
   definition-list style summary:
   - `Total: <n>` · `Open: <n>` · `In progress: <n>` · `Done: <n>` ·
   - `Last activity: <YYYY-MM-DD>` (date part of `lastActivityAt`) or
     `Last activity: none` for empty workspaces.
   - `<dl>` semantics with `<dt>/<dd>` pairs (machine-checkable).
   Refreshes on every list reload (fetches after mutations that change
   counts: create/delete/edit-with-status-change — simplest: reload summary
   together with the list).

## Public examples

- Seeded Apollo: summary = `{ totalItems: 8, byStatus: { open: 4,
  in_progress: 2, done: 2 }, lastActivityAt: "2026-11-04T10:15:00.000Z" }`
  (open: wi_101/103/105/107; in_progress: wi_102/106; done: wi_104/108).
- After deleting one open item → total 7, open 3 (fresh read via second
  connection).
- Empty workspace (cleo… no: a newly created workspace) → totalItems 0,
  zeros, `lastActivityAt: null`, UI shows `Last activity: none`.

## Boundaries & non-goals

- No overdue counts, no due-date logic, no per-member stats, no charts, no
  trends, no caching layer.

## Compatibility expectations

- Additive endpoint + UI section; list/edit flows unchanged.
- `npm run check:full` green.

## Ownership

- Owns: summary endpoint (SQL aggregates), UI collapsible panel with
  `<dl>`, api tests (seeded exact numbers + empty workspace + refresh after
  mutation) + e2e (expand → dt/dd values match; after create, values
  update).
- Must not touch: list endpoint, schema, auth.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| Aggregate correctness | api test: seeded Apollo exact JSON (total 8, open 4, in_progress 2, done 2, lastActivityAt "2026-11-04T10:15:00.000Z") |
| Empty workspace | api test: zeros + null |
| Membership | api test: non-member → 404 envelope |
| Mutation refresh | api test: create + delete cycle changes total/counts |
| UI | e2e: expand panel → dt/dd exact values; create item → values update after reload of panel |
