# S06 — Destructive-action permissions (creator or owner)

- Status: DRAFT, revision R1 (not qualified)
- Kind: scored
- Area: ownership/authorization
- Conflicts with: S13 (membership management — S13 changes who members are;
  the rule here applies to whoever is a member). Independent on the
  baseline, never combined (reset-per-task policy in `README.md`).

## Baseline behavior (explicit)

Any **member** of a workspace may update or delete any item in it — including
items they did not create, in workspaces they do not own. The `owner` role
exists (creator of the workspace) but grants no extra powers. Enforcement
currently lives in `requireItemMembership` (membership → allowed). The UI
sends **every field on PATCH** (title included) even when only one field
changed.

## Requirement

Restrict destructive and ownership-affecting changes:

1. **DELETE** `/api/items/:id`: allowed only if the caller **created the
   item** (`created_by == caller`) **or** is an **owner** of the workspace.
   Otherwise → 403 `forbidden`, message
   `"Only the item creator or a workspace owner can delete this item."`.
2. **Rename rule — actual changes only.** PATCH stays member-level for
   `notes`, `status`, `dueDate`. A `title` present in the PATCH is checked
   against the **stored** title:
   - unchanged (`patch.title === item.title`, baseline stores verbatim — no
     trimming): treated like any member-level field; the PATCH proceeds
     (this is what makes the baseline's save-all-fields UI work for
     non-renamers).
   - changed (differs from the stored title) by a member who is neither the
     creator nor an owner → 403 `forbidden` with message
     `"Only the item creator or a workspace owner can rename this item."`
     and the DB row untouched. (Rationale: titles are the item's identity
     in this product.)
   - The comparison is on the exact strings received vs stored; there is no
     trim/normalize step in this task.
3. Responses never leak: a non-member still gets 404 (unchanged); the new
   403 applies **only to members lacking the role/creator relation**.
4. UI:
   - "Delete" button renders (enabled) only for users who would be allowed
     (creator or owner). Others see a disabled button with
     `aria-label` unchanged and `title` attribute `Deletion requires the
     creator or a workspace owner.` (no tooltip library).
   - Edit mode: the Title field is disabled (with `aria-describedby` hint
     text `Renaming requires the creator or a workspace owner.`) when the
     current user may not rename; other fields stay editable and submit
     normally (the disabled Title field submits the unchanged stored title,
     which rule 2 allows).
   - The UI derives this from data it already has: add `canRename` /
     `canDelete` booleans computed into the items **list response** items
     (additive fields on each WorkItem, computed server-side from session +
     membership + created_by). Create/PATCH item responses are unchanged.

## Public examples

- Seeded Apollo: bruno (member, non-creator of wi_101 created by ada, ada is
  owner) tries `DELETE /api/items/wi_101` → 403 with the exact message;
  ada (owner) deletes → 204.
- bruno PATCHes `{"notes":"new"}` on wi_101 → 200; PATCHes
  `{"title":"Renamed"}` on wi_101 (stored title differs) → 403 rename
  message; PATCHes `{"title":"Renamed"}` on wi_104 (created by bruno) → 200.
- bruno PATCHes wi_101 with `{"title":"Draft launch checklist","notes":"x"}`
  (title present but unchanged) → 200; notes updated, no 403.
- UI: as bruno, wi_101 shows disabled Delete + disabled Title field in edit
  mode with the hint, and saving other fields from that form succeeds;
  wi_104 shows both enabled.

## Boundaries & non-goals

- No new roles, no per-item ACLs, no transfer-ownership, no member-level
  "can manage members" (S13), no change to workspace creation/role
  assignment.
- Do not introduce 403 for non-members (that stays 404).
- No audit/log of denials.
- Disclosed boundary: the rename check is value-change-based (not
  field-presence-based) exactly as specified; a member-level PATCH that
  includes an unchanged title must never 403.

## Compatibility expectations

- `version` semantics, PATCH partial rules, and delete confirm flow in the
  UI stay as baseline (the confirm step just leads to either success or the
  disabled state).
- Baseline api tests that assert "blocks mutations by non-members" (404)
  remain valid; the implementer adds member-without-permission 403 cases.
- `npm run check:full` green (no baseline test edits).

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
| Rename rule | api tests: bruno rename wi_101 (changed) → 403; rename own → 200; notes/status by any member → 200 |
| Unchanged title allowed | api test: member PATCH including the stored title verbatim + other fields → 200, no 403 |
| No leak | api test: cleo (non-member) DELETE wi_101 → 404 not 403 |
| Server-computed flags | api test: list response has canRename/canDelete matching the rules for bruno and ada |
| UI | e2e: as bruno, wi_101 Delete disabled + rename hint; saving other fields from the edit form succeeds; own item fully editable |
