# C4 — Remember last workspace (calibration)

- Status: DRAFT, revision R1 (not qualified)
- Kind: calibration
- Area: client persistence
- Conflicts with: S10 (switch guard) — S10 governs unsaved-draft behavior on
  switch; this task governs cross-session selection only. Independent on the
  baseline, never combined (reset-per-task policy in `README.md`).

## Baseline behavior

Workspace selection lives in React state; every load selects the first
workspace in name order (e.g. bruno always lands on "Apollo Launch").

## Requirement

Persist the last selected workspace as a **last-user single slot** and
restore it (this is NOT a multi-user store: the key holds one
`{ userId, workspaceId }` pair belonging to whichever user saved last, and
is overwritten on every save by any user):

1. When the user selects a workspace, store `{ userId, workspaceId }` under a
   single `localStorage` key `workboard.last-workspace` (overwrite on every
   change — including when a different user overwrites a previous user's
   entry).
2. On load, after `/api/me` resolves: restore the stored workspace only if
   the stored `userId` matches the signed-in user AND the workspace is still
   in their membership list; otherwise fall back to baseline (first
   workspace). Mismatch isolation therefore only holds for the currently
   signed-in user while their entry is still stored; a later user's
   selection overwrites it (disclosed single-slot limitation).
3. A stale/mismatched entry must never break the app (wrap parse; treat any
   malformed value as absent).
4. `Sign out` must NOT clear the key (it is a last-user preference slot;
   mismatch protection in (2) is the safety net).

## Public examples

- bruno selects "Borealis Ops", reloads → "Borealis Ops" is selected (was
  "Apollo Launch" in baseline).
- In the **same browser context**: bruno selects "Borealis Ops" (key now
  holds bruno's pair), signs out, signs in as ada → the stored `userId` is
  bruno's, so ada gets "Apollo Launch" (mismatch fallback against an
  existing, non-stale key).
- ada then selects any workspace → the key is overwritten with ada's pair;
  bruno signing back in falls back to "Apollo Launch" for the same reason.
- Corrupt `localStorage` value (`"{{{"`) → app loads normally on the first
  workspace.

## Boundaries & non-goals

- No cookies, no server-side preference endpoint, no per-workspace item
  scroll restoration, no storage of filters/sort.
- sessionstorage is explicitly NOT used (the requirement says localStorage).
- No multi-user store, no per-user keys, no migration of old formats: one
  key, last writer wins, mismatch fallback is the only isolation mechanism
  (disclosed limitation, tested as specified above).

## Compatibility expectations

- Fresh browser profile behaves exactly as baseline (key absent → first
  workspace).
- `npm run check:full` stays green.

## Ownership

- Owns: storage read/write helpers (pure, unit-tested with an injected
  storage facade under `tests/unit`), selection effect in
  `src/components/Workboard.tsx`, new e2e test using `page.evaluate` to
  seed/inspect localStorage.
- Must not touch: API, schema, auth, seed.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| Restore on reload | e2e: select Borealis, reload → Borealis selected (bruno) |
| Mismatch guard, same context | e2e: bruno stores selection, sign out, ada signs in **in the same storage context** → Apollo selected (key present with bruno's userId) |
| Key-absent path | e2e: fresh context, ada signs in → Apollo selected (baseline behavior) |
| Corrupt value | e2e: set invalid value, load → first workspace, no crash |
| Key format | unit test: shape `{ userId, workspaceId }` under exact key name |
