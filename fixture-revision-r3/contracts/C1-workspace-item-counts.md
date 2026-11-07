# C1 — Workspace item counts (calibration)

- Status: DRAFT, revision R3 (not qualified)
- Kind: calibration
- Area: full-stack, small
- Conflicts with: S14 (summary aggregation) — independent on the baseline;
  runs on a freshly reset baseline (see `README.md` execution model)

## Baseline behavior

`GET /api/me`, `GET /api/workspaces`, and `GET /api/workspaces/:id` return
workspace metadata only — no item counts. The UI workspace selector shows
plain names. There is no count column, no aggregate SQL, and no badge.

## Requirement

Surface an **open-item count** (status `open`) per workspace:

1. `GET /api/me` and `GET /api/workspaces` responses gain an integer
   `openItemCount` per workspace (count of `work_items` in that workspace
   with `status = 'open'`).
2. The UI workspace selector option text becomes `"<name> (<count>)"` —
   e.g. `Apollo Launch (4)`. (Seed: Apollo has 4 open, Borealis has 3 open.)
3. Counts must come from the database at request time (no caching, no
   denormalized column required — a single aggregate query or JOIN GROUP BY
   is fine).

## Public examples

- As ada: `GET /api/me` → `workspaces[0]` = `{ "id": "ws_apollo", "name":
  "Apollo Launch", "role": "owner", "createdAt": "...", "openItemCount": 4 }`.
- As ada: after creating item "Temp probe" (status open) in ws_apollo, a
  fresh `GET /api/me` shows `openItemCount: 5`; after PATCHing it to `done`,
  a fresh `GET /api/me` shows `4` again.
- UI: selector for bruno reads `Apollo Launch (4)` / `Borealis Ops (3)`;
  adding one open item in Borealis makes it `Borealis Ops (4)` after reload.

## Boundaries & non-goals

- No counts for other statuses; no total counts in the workspace detail
  response; no badge next to the role text; no dashboard; no caching.
- Do not change item list behavior, ordering, or the `WorkItem` shape.
- Do not add filters or search.

## Compatibility expectations

- All baseline endpoints keep their existing fields; `openItemCount` is
  additive on the two list/me responses only.
- `npm run check:full` stays green with only the public migrations below.
  They preserve the same membership/order assertions and switch targets;
  all other tests, actions, barriers and feedback checks stay untouched.

### Enumerated public test migrations (exhaustive by assertion/selector)

- `e2e/auth.spec.ts`: the three seeded workspace option-text array
  assertions become `["Apollo Launch (4)"]`, `["Borealis Ops (3)"]`,
  `["Apollo Launch (4)", "Borealis Ops (3)"]`; the fresh sign-up option
  assertion becomes `["Dora Lab (0)"]`. These run before mutations in the
  public suite. Keep all role and membership assertions.
- `e2e/ownership.spec.ts` and `e2e/switch.spec.ts`: **every** workspace
  `selectOption({ label: "Borealis Ops" })` or
  `selectOption({ label: "Apollo Launch" })` may be replaced respectively
  with `selectOption("ws_borealis")` or `selectOption("ws_apollo")`. These
  are the actual option values. This includes delayed and failed list loads,
  held create/delete and every return selection. Do not change any other
  selector (in particular item status), route, action or assertion. Selection
  by stable value is necessary because counts can differ after mutations or
  refreshes; it does not hard-code a stale count. The new
  `e2e/isolation.spec.ts` already uses these values and needs no migration.
- No API assertion migration is needed: existing tests assert workspace
  fields or projections, not an exact response object key set. No other
  baseline test edits are permitted.

## Ownership

- Owns: additive changes in `server/api.ts` (me/workspaces responses), the
  selector option rendering in `src/components/Workboard.tsx`, and minimal
  updates to affected tests.
- May add: one unit test for the count helper if extracted to `shared/`.
- Must not touch: auth, seed data, schema DDL (no new columns needed), the
  baseline contract.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| Count in `/api/me` + `/api/workspaces` | api test: seeded DB → exact counts Apollo 4 open, Borealis 3 open; create+done cycle updates count |
| Selector text | e2e: options text `[Apollo Launch (4), Borealis Ops (3)]` for bruno |
| DB-derived | api test: create → count+1; PATCH done → count back to base |
| Baseline intact | `npm run check:full` exit 0 (with only the enumerated assertion/selector migrations above) |
