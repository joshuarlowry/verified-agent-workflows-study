# C4 — Remember last workspace (calibration)

- Status: DRAFT (not qualified)
- Kind: calibration
- Area: client persistence
- Conflicts with: S10 (switch guard) — S10 governs unsaved-draft behavior on
  switch; this task governs cross-session selection only. Independent on the
  baseline.

## Baseline behavior

Workspace selection lives in React state; every load selects the first
workspace in name order (e.g. bruno always lands on "Apollo Launch").

## Requirement

Persist the last selected workspace **per user** and restore it:

1. When the user selects a workspace, store `{ userId, workspaceId }` under a
   single `localStorage` key `workboard.last-workspace` (overwrite on every
   change).
2. On load, after `/api/me` resolves: restore the stored workspace only if
   the stored `userId` matches the signed-in user AND the workspace is still
   in their membership list; otherwise fall back to baseline (first workspace).
3. A stale/mismatched entry must never break the app (wrap parse; treat any
   malformed value as absent).
4. `Sign out` must NOT clear the key (it is a per-user preference store;
   mismatch protection in (2) is the safety net).

## Public examples

- bruno selects "Borealis Ops", reloads → "Borealis Ops" is selected (was
  "Apollo Launch" in baseline).
- bruno selects "Borealis Ops", signs out, signs in as ada → ada gets "Apollo
  Launch" (stored entry is bruno's → mismatch fallback).
- Corrupt `localStorage` value (`"{{{"`) → app loads normally on the first
  workspace.

## Boundaries & non-goals

- No cookies, no server-side preference endpoint, no per-workspace item
  scroll restoration, no storage of filters/sort.
- sessionstorage is explicitly NOT used (the requirement says localStorage).

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
| Per-user guard | e2e: bruno stores selection; ada signs in (fresh context) → Apollo selected |
| Corrupt value | e2e: set invalid value, load → first workspace, no crash |
| Key format | unit test: shape `{ userId, workspaceId }` under exact key name |
