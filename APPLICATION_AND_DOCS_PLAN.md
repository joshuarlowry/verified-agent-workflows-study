# Application and documentation preparation — draft revision 4

The proposed application is **Workboard Lab**, a small work-item tracker with a real React UI, HTTP API, session authentication and a disposable SQLite database. Use one TypeScript application to keep setup manageable while retaining meaningful UI/API/persistence/ownership work. This document selects a candidate stack and turns Context setup into an ordered work plan. It does not author the benchmark application or its acceptance tests.

## Proposed stack and documentation

Package versions below were confirmed in the npm registry on 2026-11-07 UTC. They are candidate pins for independent qualification, not a tested lockfile. See [machine-readable source metadata](docs/corpus-plan.json). Node 24.19.0 and npm 10.9.0 are the observed development versions; the qualified runtime image will pin their actual artifacts.

| Layer | Candidate | Documentation to supply |
|---|---|---|
| UI and HTTP API | Next.js 16.4.5 App Router | Routes, route handlers, request/response APIs, server/client boundaries, forms, error handling, caching and framework configuration |
| UI runtime | React and React DOM 19.3.1 | State, controlled inputs, effects, events, accessibility and rendering APIs |
| Language | TypeScript 5.9.3 | Narrowing, nullability, types and compiler configuration; deliberately retain this known major version pending builder review |
| Authentication | Better Auth 1.7.18 | Local email/password sessions, server-side session lookup, Next integration, SQLite adapter, cookies and schema generation |
| Persistence | better-sqlite3 13.0.3 plus its linked SQLite engine | Prepared statements, parameter binding, transactions, foreign keys and SQLite constraints/date behavior |
| Unit/domain checks | Vitest 5.1.0 | Runner/configuration, setup, mocks and isolation |
| UI and HTTP integration checks | Playwright Test 1.65.0 | Role/label locators, assertions, fixtures, browser isolation, API requests and traces |
| Static checks | ESLint 10.14.0 and eslint-config-next 16.4.5 | Flat configuration, relevant rule references and framework linting |
| Runtime | Node.js 24.19.0 candidate | File/path/process APIs, HTTP/fetch and runtime behavior used by the fixture |
| Local application knowledge | Frozen public baseline docs | Repository instructions, development/reset/check commands, public API/schema contracts and conventions |

Use CSS modules/plain CSS initially; avoid additional component libraries, hosted infrastructure and a separate ORM unless independent construction demonstrates a concrete need. Plan numbered SQL schema changes and reproducible reset commands for disposable databases. The builder must choose and document authentication schema setup and the exact linked SQLite version. Seeding/auth setup and test-data mutation await the protocol's disposable-database authorization gate.

This is a proposal that an eligible builder must validate. Confirm native SQLite module installation on the chosen image, framework/auth integration, peer compatibility, Next build, standalone typecheck, ESLint, Vitest and Playwright against a real temporary database. Pin browser binaries, transitive dependencies and relevant type packages in the lockfile, matching Node/React versions rather than taking unrelated latest types. A package's presence in the registry does not prove compatibility. Any failed qualification changes the candidate pins before calibration, with the reason recorded.

## What the existing Context setup establishes

The local `library-docs` entry launches `@neuledge/context` 1.3.3. A direct MCP check initialized the server, listed only `get_docs` under its configured exact-version allowlist, and retrieved Next.js route-handler documentation successfully. The exposed libraries were `next@16.4.0`, `better-auth@1.7.7`, `vitest@5.0.4` and `python-stdlib@3.14`. This verifies local server operation; study-role adapters and offline isolation remain unqualified.

Refresh Next, Better Auth and Vitest documentation for the candidate pins. Add React/React DOM, TypeScript, better-sqlite3/SQLite, Playwright, ESLint and Node coverage. Exclude Python from this application's corpus. Do not assume a registry package exists for each exact pin: resolve its real Context ID or build it from approved source. Record this resolution in `docs/corpus-manifest.json` rather than inventing library IDs now.

Prefer release-tagged official sources and package-bundled documentation. Where a project's website describes a release family rather than an exact patch, archive the dated source revision and explicitly declare coverage. Check each relevant API against the pinned package/types/release notes. A package name ending in a version must not imply patch-specific documentation that was never verified.

Context 1.3.3's installed source resolves its package store under the OS home directory (`~/.context/packages`). Do not rely on an undocumented cache-directory flag. Use a dedicated container or OS identity with only the approved corpus mounted there, no inherited credentials and independent writable state. Keep the host's existing Context installation intact. Pin the Node runtime used by the server separately from the application if necessary and disclose it.

## Ordered work packages and evidence

| Step | Owner | Work and completion evidence |
|---|---|---|
| 1. Validate stack | Eligible fixture builder; independent qualifier | Confirm candidate compatibility, image and lockfile; register changes and exact runtime/SQLite/browser versions. Builder provenance and family-exclusion checks pass. |
| 2. Inventory sources | Documentation curator; independent reviewer | Map every required topic to official source revision, version coverage and license. Record missing exact-version packages and approved custom-build inputs. No reference solution or sealed check enters the corpus. |
| 3. Build corpus | Mechanical setup controller from reviewed sources | Prefetch/build Context packages, export the same read-only source docs for file tools, and hash archives, source snapshots, extraction settings and indexes. Record actual Context IDs. |
| 4. Configure adapters | Harness maintainer | Launch Context with explicit exact-version `--libs` entries in dedicated identities. Generate Codex/OpenCode configurations and broker inheritance from one manifest. Configure other relevant MCP candidates under MCP_SETUP.md; freeze inclusion decisions. |
| 5. Qualify retrieval | Harness maintainer; independent reviewer | Run the common query suite offline, verify citations/version coverage, catalog restriction, forbidden-source rejection and consistent source access in all seven roles below. Store timing/errors and raw evidence. |
| 6. Freeze and rehearse | Coordinator; independent signoff | Publish sanitized manifests/hashes and resolve all gaps. Smoke the task launch, worker handoff, MCP failure behavior and full public checking protocol. Freeze before calibration; no task-dependent operator hints. |

The coordinator may plan, collect package metadata and perform transport/setup work. The existing family exclusion still applies to constructing the baseline, reference/alternative implementations and acceptance checks. Documentation curation must not introduce model-written benchmark solutions or task-specific repair hints. These planning steps do not appoint the coordinator as an eligible fixture builder.

## Cross-agent parity checklist

| Session role | Current proposed harness | Required evidence |
|---|---|---|
| Gemma direct | OpenCode | Common tool schema, corpus hash and retrieval/isolation results |
| GLM direct | OpenCode | Same |
| Terra direct | Codex | Same; native adapter differences recorded |
| Terra supervisor | Codex | Same; role permissions still enforce Gemma-only application/test edits |
| GLM supervisor | OpenCode | Same; role permissions still enforce Gemma-only application/test edits |
| Gemma under Terra | OpenCode via fixed broker | Same; new worker session inherits the frozen manifest |
| Gemma under GLM | OpenCode via fixed broker | Same; new worker session inherits the frozen manifest |

The transport readiness of Terra through OpenRouter does not itself change this proposed matrix. A common-OpenCode design requires its own explicit protocol revision; either design must pass this same capability/corpus checklist.

The setup query suite covers route handlers, controlled UI state, type narrowing, server sessions, bound SQL parameters, transaction rollback, Vitest setup/mocks, semantic browser locators, HTTP test requests, lint configuration, Node APIs and public repository instructions. These are generic documentation lookups, not task-specific reference answers. Freeze exact query strings and acceptable source/section IDs once sources exist, before any model runs. Negative probes request an unlisted library, a wrong version, an outside-corpus path and another repository. Inspect actual catalogs and filesystem/network access as well as returned text: prompt instructions alone do not establish isolation.

Record pass/fail/unverified for each role × query and each isolation/failure check. A positive query needs relevant source-backed content, correct declared version coverage and no retrieval error; empty, unrelated or unattributed output fails. Negative probes must not disclose forbidden content. Timeouts and unavailable docs must produce logged, bounded errors under the same policy across roles. Resolve any missing required coverage before signing the documentation gate; report optional coverage exclusions explicitly.

## Definition of setup completion

All candidate versions are either qualified and locked or replaced with recorded reasons; every required documentation topic has reviewed source coverage; all seven role adapters pass their applicable checks; the same corpus and tool manifest reach workers; offline and filesystem isolation pass; MCP timing/usage capture works; and registration evidence hashes and independent signoffs are populated. Until then the status is **planned, not launchable**.

Public output is the sanitized inventory, final corpus manifest, common MCP manifest, qualification matrix and coverage gaps. Source archives are distributed only where their licenses permit; retain private evidence hashes where publication is restricted. Runtime retrieval counts toward the workflow deadline, while source collection/indexing and setup review are reported as preparation overhead.

Reference entry points: [Next.js installation](https://nextjs.org/docs/app/getting-started/installation), [Better Auth SQLite integration](https://better-auth.com/docs/adapters/sqlite), [Playwright semantic locators](https://playwright.dev/docs/locators), [Context source](https://github.com/neuledge/context). The final corpus needs versioned snapshots rather than these mutable links alone.
