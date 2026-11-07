# S06 — Destructive-action permissions (creator or owner)

- Status: DRAFT (not qualified)
- Kind: scored
- Area: ownership/authorization
- Conflicts with: S13 (membership management — S13 changes who members are;
  the rule here applies to whoever is a member). Independent on the baseline.

## Baseline behavior (explicit)

Any **member** of a workspace may update or delete any item in it — including
items they did not create, in workspaces they do not own. The `owner` role
exists (creator of the workspace) but grants no extra powers. Enforcement
currently lives in `requireItemMembership` (membership → allowed).

## Requirement

Restrict destructive and ownership-affecting changes:

1. **DELETE** `/api/items/:id`: allowed only if the caller **created the
   item** (`created_by == caller`) **or** is an **owner** of the workspace.
   Otherwise → 403 `forbidden`, message
   `"Only the item creator or a workspace owner can delete this item."`.
2. **Title/status/due-date changes stay member-level** (any member can still
   PATCH basic fields) **except** a PATCH that changes `title` of an item
   whose `created_by != caller`: allowed, but the response is unchanged…
   (no — keep it simple):
   - PATCH stays member-level for `notes`, `status`, `dueDate`.
   - PATCH of `title` by a member who is neither creator nor owner → 403
     with message `"Only the item creator or a workspace owner can rename
     this item."`. (Rationale: titles are the item's identity in this
     product.)
3. Responses never leak: a non-member still gets 404 (unchanged); the new
   403 applies **only to members lacking the role/creator relation**.
4. UI:
   - "Delete" button renders (enabled) only for users who would be allowed
     (creator or owner). Others see a disabled button with
     `aria-label` unchanged and `title` attribute `Deletion requires the
     creator or a workspace owner.` (no tooltip library).
   - Edit mode: the Title field is disabled (with the same hint as
     `aria-describedby` text `Renaming requires the creator or a workspace
     owner.`) when the current user may not rename; other fields stay
     editable.
   - The UI must derive this from data it already has: add `canRename` /
     `canDelete` booleans computed into the items list response items
     (`canRename`, `canDelete` additive fields on each WorkItem) — computed
     server-side from session + membership + created_by.

## Public examples

- Seeded Apollo: bruno (member, non-creator of wi_101 created by ada, ada is
  owner) tries `DELETE /api/items/wi_101` → 403 with the exact message;
  ada (owner) deletes → 204.
- bruno PATCHes `notes` of wi_101 → 200; PATCHes `title` of wi_101 → 403
  rename message; PATCHes `title` of wi_104 (created by bruno) → 200.
- UI: as bruno, wi_101 shows disabled Delete + disabled Title field in edit
  mode with the hint; wi_104 shows both enabled.

## Boundaries & non-goals

- No new roles, no per-item ACLs, no transfer-ownership, no member-level
  "can manage members" (S13), no change to workspace creation/role
  assignment.
- Do not introduce 403 for non-members (that stays 404).
- No audit/log of denials.

## Compatibility expectations

- `version` semantics, PATCH partial rules, and delete confirm flow in the
  UI stay as baseline (the confirm step just leads to either success or the
  disabled state).
- Baseline api tests that assert "blocks mutations by non-members" (404)
  remain valid; the implementer adds member-without-permission 403 cases.
- `npm run check:full` green.

## Ownership

- Owns: authorization helper (`shared/` pure role logic + unit tests),
  `server/api.ts` PATCH/DELETE gates + `canRename`/`canDelete` fields,
  `Workboard.tsx` conditional buttons/disabled fields + hint, api + e2e
  tests using seeded cross-user fixtures (bruno/ada).
- Must not touch: schema, seed data, auth, membership endpoints.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| Delete rule | api tests: bruno→wi_101 403 exact message; ada→204; bruno deletes own wi_104 → 204 |
| Rename rule | api tests: bruno rename wi_101 → 403; rename own → 200; notes/status by any member → 200 |
| No leak | api test: cleo (non-member) DELETE wi_101 → 404 not 403 |
| Server-computed flags | api test: list response has canRename/canDelete matching the rules for bruno and ada |
| UI | e2e: as bruno, wi_101 Delete disabled + rename hint; own item fully editable |
