# C3 — Item share link: clipboard + deep link (calibration)

- Status: DRAFT, revision R1 (not qualified)
- Kind: calibration
- Area: UI state, navigation
- Conflicts with: S10 (switch guard), S15 (focus) — different surfaces;
  independent on the baseline, never combined (reset-per-task policy in
  `README.md`).

## Baseline behavior

The UI keeps `selectedId` (workspace) in React state only; there are no URLs
beyond `/`, no clipboard usage, and no way to jump back to an item after a
reload. Deep-linking does not exist.

## Requirement

Add a minimal share/deep-link flow for a work item:

1. Each item row gains a **"Copy link"** button (aria-label `Copy link
   <title>`). Clicking it writes a URL of the form
   `<origin>/?workspace=<workspaceId>&item=<itemId>` to the clipboard and the
   live region announces `Link copied.` (No toast; the existing
   `role="status"` region is the feedback channel. Clipboard may use
   `navigator.clipboard` with an in-page fallback of selecting… no — keep it
   simple: use `navigator.clipboard.writeText`; e2e grants clipboard
   permissions.)
2. On load, the app parses `?workspace=&item=` **only after the session
   check resolves and the user is signed in** (signed-out visitors see the
   baseline sign-in screen first; the query string stays in the address bar
   untouched until sign-in completes, after which the link is applied
   normally by the same rule):
   - If the signed-in user is a member of `workspace` and `item` exists in
     it: select that workspace, load items, and **scroll the item into view
     with a visible highlight** (`outline` or background flash class for ≥1s).
   - If the user is not a member (or ids unknown): show the existing app but
     with an error banner `role="alert"` text exactly `Linked item is not
     available.` and normal (first) workspace selection.
   - **Malformed/partial links follow the same unavailable path**: a query
     string with a missing, empty, or malformed `workspace` or `item`
     value, or extra unrelated parameters, is treated exactly like an
     unavailable link (exact banner text + first-workspace fallback) —
     never a crash, never a blank screen.
3. URL cleanup: after applying (either branch above), remove the query
   string from the address bar (history.replaceState) so reloads return to
   plain `/`. For a signed-out visitor the query string is left as-is.
4. **Clipboard failure policy**: `navigator.clipboard.writeText` may reject
   (permission denied, unsupported context). On failure the app shows an
   error banner `role="alert"` with text exactly `Could not copy the link.`
   and the live region is NOT used for this error; no partial URL is
   announced as copied.

## Public examples

- ada opens `/`, copies the link for "Draft launch checklist" → reload with
  that URL → Apollo selected, the checklist card has a temporary highlight,
  address bar shows `/` afterwards.
- cleo opens an ada-copied link → banner "Linked item is not available." and
  Borealis selected (cleo's only workspace).

## Boundaries & non-goals

- No routing library, no per-item route path, no share dialog/modal, no
  permission changes (links only work for members), no short links/tokens.
- No persistence of the highlight beyond the temporary class.
- Do not change item CRUD or the two-step delete.
- Disclosed edge boundaries (part of the contract, not scope creep):
  clipboard failures → the exact alert above; malformed/partial query
  strings → the unavailable path; the query string is applied at most once
  per page load (no re-application on client-side navigation, which the
  baseline does not have); the app never writes clipboard content on the
  unavailable path.

## Compatibility expectations

- Direct visits to `/` behave exactly as baseline (no query parsing errors).
- Signed-out visits with a link query behave exactly as baseline sign-in
  (no errors before sign-in).
- `npm run check:full` stays green.

## Ownership

- Owns: URL parse/apply logic (suggest a small pure helper in `src/` with a
  unit test or a vitest test under `tests/unit`), "Copy link" button in
  `ItemListView`/`Workboard`, highlight CSS in `styles.css`, new e2e tests
  (including clipboard permission context in `playwright.config.ts` if
  needed).
- Must not touch: API responses, schema, auth.

## Acceptance mapping

| Requirement | Observable check |
|---|---|
| Link format + copy | e2e: click Copy link → clipboard content matches pattern; live region announces |
| Member deep link | e2e: reload with URL → workspace selected + item highlighted; query string cleared |
| Non-member deep link | e2e: cleo with ada's link → exact alert text, own workspace shown |
| Malformed link | e2e: missing/malformed `workspace`/`item` params → exact alert, first workspace, no crash |
| Signed-out link | e2e: signed-out visit with link URL → sign-in screen shown, no error; after sign-in the link applies |
| Clipboard failure | e2e: deny clipboard permission context → exact `Could not copy the link.` alert |
| Baseline intact | `npm run check` exit 0 |
