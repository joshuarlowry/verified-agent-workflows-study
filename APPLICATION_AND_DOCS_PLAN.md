# Application and documentation work plan

The architecture, exact candidate package pins and runtime live only in [registration.json](registration.json), `application_preparation`. This replaces the earlier Next.js proposal. Package metadata confirms availability, not a working lockfile.

Use a small React UI built with Vite and a separate Hono HTTP API on Node, with SQLite persistence and library-backed sessions. A development proxy and qualified static/API serving should preserve same-origin browser behavior. This keeps request, ownership and persistence boundaries explicit while avoiding framework server/client and caching conventions. Candidate versions and integration still require independent builder qualification; a simpler framework does not eliminate model training familiarity effects.

## Work sequence

| Work | Owner | Exit evidence |
|---|---|---|
| App fixture and dependency qualification | Eligible builder outside subject families; independent qualifier | Locked runtime/dependencies/browser/SQLite engine; native module install, UI/API/database/auth integration, reset and public check commands replay cleanly |
| Documentation source selection | Named curator; independent content reviewer outside subject families | Reviewed source inventory and omissions, version/API coverage, licenses, extraction checks and absence of benchmark solutions |
| Context packaging and common adapter | Mechanical maintainer using approved sources | Approved package IDs/hashes and read-only files; one OpenCode adapter; isolated storage and role inheritance |
| Calibration task/evaluator qualification | Eligible builders and independent qualifier | Reference/alternate paths, negative controls, clean replay and contract/check signoffs |
| Rehearsal | Coordinator and eligible independent qualifiers | Broker/usage capture, evaluator and core launch gates pass; human patch-review staffing is optional |

Documentation topics cover Vite configuration/proxy/build, React state/inputs/events, TypeScript narrowing/nullability, Hono requests/responses/middleware, Node serving, session cookies and server lookup, bound SQLite statements/transactions/constraints, Vitest setup/mocks, Playwright semantic locators/HTTP tests, lint configuration and public repository/API/schema conventions. Exclude old Next and Python documents from the application corpus. Exact query strings and acceptable source sections are frozen after independently reviewed source selection, before subject runs.

Where official docs describe a release family, record the snapshot/source revision and validate relevant APIs against pinned packages/types; never relabel unverified prose as exact patch coverage. Missing Context packages may be built from approved official inputs without adding a RAG server. Underlying Context lexical retrieval introduces no extra model.

The coordinator may plan and perform approved mechanical setup. It may not build the application, references or acceptance suite under the subject-family exclusion, nor independently approve the corpus it proposed. Independent fixture/corpus qualifiers may be eligible humans or models outside subject families, with provenance recorded. Human patch-review names and capacity are needed only before an optional review extension, not before core calibration.

No stack installation, fixture construction or corpus content approval is completed by this plan. See [MCP_SETUP.md](MCP_SETUP.md) for the compact procedure and [TASK_TEMPLATE.md](TASK_TEMPLATE.md) for task evidence.
