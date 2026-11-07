# S09 — Optimistic concurrency: version hints, 409, conflict UX

- Status: DRAFT (not qualified)
- Kind: scored
- Area: version conflicts
- Conflicts with: S12 (activity history) — history may record version; S07
  (failed-save recovery — conflict UX composes with it). Independent on the
  baseline.

## Baseline behavior (explicit)

`work_items.version` starts at 1 and increments on every successful PATCH,
but PATCH is **last-write-wins**: no version hint is accepted, no 409 exists,
and a stale client silently overwrites newer changes. `conflict` is a
reserved error code with no producer.

## Requirement

Add conditional updates with a defined conflict flow:

1. **Request**: `PATCH /api/items/:id` accepts an optional
   `expectedVersion` (positive integer). Baseline requests without it keep
   baseline behavior (LWW, no hint).
2. **Conflict**: with `expectedVersion` supplied and `expectedVersion !==
   item.version` → `409 {"error":{"code":"conflict","message":"This item
   was changed by someone else. Reload to see the latest version.",
   "fields":{"currentVersion":"<n>","currentItem":<full fresh WorkItem>}}}`;
   the DB row is **not** modified, `version` unchanged.
3. **Match**: `expectedVersion === version` → normal update (version+1) —
   race-safe via a single conditional `UPDATE ... WHERE id = ? AND version
   = ?` and a check of `changes`; a lost race returns the 409 above.
4. **Validation**: `expectedVersion` present but not an integer ≥ 1 → 400
   `fields.expectedVersion = "expectedVersion must be a positive integer."`.
5. **UI edit flow**: when opening the edit form, capture the item's
   `version`; submit with `expectedVersion`. On 409:
   - alert (role="alert") shows the server message exactly;
   - the form **stays open with the user's input preserved**;
   - an added **"Reload latest"** button (inside the alert block) re-reads
     the item and refills the form with fresh server values (draft replaced
     — documented destructive refresh), then the user can re-save.
6. The create form and delete flow are unchanged (deletes stay LWW).

## Public examples

- Fresh item (version 1): PATCH with `{expectedVersion:1, title:"A"}` → 200,
  `version:2`. Immediately PATCH again with `{expectedVersion:1, ...}` → 409
  with `fields.currentVersion = "2"`; fresh-connection read proves title
  unchanged by the rejected call.
- PATCH **without** expectedVersion after the same history → 200 (baseline
  LWW path intact).
- `{"expectedVersion":"two"}` → 400 with the exact field message.
- e2e: open edit form for an item; second browser context PATCHes the same
  item; first context saves → conflict alert + preserved input; click
  "Reload latest" → form shows the other context's title; save succeeds.

## Boundaries & non-goals

- No merge UI/diff view, no change history (S12), no If-Match HTTP header
  semantics, no ETags, no conditional CREATE/DELETE, no retry loops.
- No change to list responses (version already present).

## Compatibility expectations

- Requests without `expectedVersion` behave exactly as baseline (all
  baseline tests keep passing untouched — this task adds, not changes).
- `npm run check:full` green.

## Ownership

- Owns: `server/api.ts` conditional update path (+ shared pure helper for
  conflict payload, unit-testable), `ItemForm` version capture/submit +
  conflict alert + "Reload latest", api tests (match/stale/invalid/DB
  unchanged) + e2e two-context conflict test.
- Must not touch: schema (version column exists), seed data, auth, delete.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| Conditional update | api test: match → version+1; stale → 409 + DB unchanged + currentItem fresh |
| Race safety | api test: two rapid PATCHes with same expectedVersion → exactly one 200, one 409 |
| LWW unchanged | api test: no-hint PATCH still succeeds after others' edits |
| Validation | api test: bad expectedVersion → 400 exact field message |
| UI conflict UX | e2e: two-context scenario → exact alert, preserved input, Reload latest refills, save succeeds |
