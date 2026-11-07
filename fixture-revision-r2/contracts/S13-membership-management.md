# S13 — Owner-managed memberships (invite + remove)

- Status: DRAFT (not qualified)
- Kind: scored
- Area: ownership/roles
- Conflicts with: S06 (authorization rules apply to whoever is a member).
  Independent on the baseline.

## Baseline behavior

Memberships are created only by seed/workspace creation; there is no way to
add or remove a member. Roles are fixed at creation (creator → owner). No
endpoint lists members.

## Requirement

Let workspace owners manage members:

1. `GET /api/workspaces/:id/members` (member) →
   `200 { members: [{ userId, email, name, role, joinedAt }] }` ordered
   `joinedAt ASC, email ASC` (joinedAt = membership created_at). Data joined
   from Better Auth's user table.
2. `POST /api/workspaces/:id/members` (**owner only**), body
   `{ "email": "user@example.test" }`:
   - target must be an **existing** account (404 `not_found`, message
     `"No account with that email."` if absent),
   - already a member → 409 `conflict`, `"That user is already a member."`,
   - owner cannot be removed/demoted here (no self-removal endpoint),
   - success → `201` member row with `role:"member"`.
3. `DELETE /api/workspaces/:id/members/:userId` (**owner only**) → removes
   the membership row; `204`. Removing the last owner → 409 `conflict`
   `"A workspace needs an owner."`. Removing a non-member → 404.
4. Authorization errors: member (non-owner) calling owner-only routes → 403
   `forbidden`, message `"Only the workspace owner can manage members."`
   (non-members still get 404).
5. After removal, the removed user loses access immediately: their
   `/api/me` no longer lists the workspace; item routes return 404 (and
   their items remain, owned by the workspace).
6. UI:
   - Workspace section gains a **"Members"** disclosure button
     (`aria-expanded`) visible to all members; panel lists members as
     `email — role` (Owner/Member labels) with joined date.
   - Owners additionally see an email `<input aria-label="Invite by email">`
     + **"Add member"** button, and **"Remove"** buttons
     (aria-label `Remove <email>`) for non-owner members only; owners are
     never removable in the UI.
   - Success/failure via the live region (`role="status"`:
     `Member added.` / `Member removed.`) and `role="alert"` for errors.

## Public examples

- ada (owner, Apollo): `POST .../members {"email":"cleo@workboard.test"}` →
  201; cleo's `/api/me` now lists Apollo Launch (role member); cleo can read
  `GET /api/workspaces/ws_apollo/items`.
- Repeat invite → 409 exact message. Unknown email → 404 exact message.
- bruno (member) calls the invite route → 403 exact message.
- ada removes cleo → 204; cleo's item routes on ws_apollo → 404; cleo's
  `/api/me` lacks Apollo.
- Borealis (bruno owner): invite ada → fine; attempt to remove bruno
  (self/owner) via member id → 409 `"A workspace needs an owner."` (only
  owner; last-owner rule).

## Boundaries & non-goals

- No email sending/invitation tokens, no pending invites, no role changes
  of existing members (no promote/demote), no leaving workspaces by
  members, no multi-owner support, no signup-on-the-fly.

## Compatibility expectations

- Seeded memberships unchanged; membership model (roles) unchanged.
- `npm run check:full` green.

## Ownership

- Owns: three endpoints + authorization helper updates, UI members panel,
  api tests (all status paths + immediate-revocation checks with two real
  sessions) + e2e (invite → other user sees workspace; remove → gone).
- Must not touch: schema (uses existing tables), seed, auth internals.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| List members | api test: seeded Apollo members exact list (ada owner, bruno member) with emails |
| Invite | api tests: 201 + target /api/me reflects it; 409 duplicate; 404 unknown; 403 non-owner |
| Remove | api tests: 204 + immediate 404s for removed user; 409 last-owner; 404 non-member |
| Envelope discipline | api test: non-member caller → 404 (not 403) on all three routes |
| UI | e2e: owner invites cleo by email (cleo sees Apollo after re-login), removes cleo (cleo loses it) |
