# MCP and documentation setup — draft revision 3

Configure and qualify one common MCP bundle before calibration. Every direct agent, supervisor and Gemma worker receives the same relevant capabilities and documentation corpus. Setup is an explicit study milestone with evidence; an installed server is only a candidate until its isolation and harness adapters pass.

## Available candidates

The following launchers are present in the development box's OpenCode configuration as of 2026-11-07 UTC. Package versions below were read from installed package metadata. Presence does not establish health, model usability or suitability for the study.

| Existing server name | Implementation observed | Proposed use and qualification |
|---|---|---|
| `library-docs` | `@neuledge/context` 1.3.3 | Required documentation capability: scope Context to exact library versions selected from the benchmark lockfile; audit its packages before exposure |
| `local-docs` | `mcp-local-rag` 0.21.3 | Index the approved local documentation snapshot if Context cannot cover it; freeze the retrieval backend and prevent duplicate, inconsistent corpora |
| `serena` | Local launcher; underlying version not yet frozen | Repository navigation candidate; verify task-only project roots, index isolation and any editing tools before inclusion |
| `gitnexus` | `gitnexus` 1.6.12 | Repository graph candidate; build a fresh task-only index without global repository discovery or prior-history access |
| `lightpanda` | Local Python launcher; engine/server versions not yet frozen | Browser candidate; qualify against the local application and semantic UI contracts, including keyboard/accessibility needs |

Configure each relevant candidate in an isolated qualification environment. Include only servers that add a necessary capability and work equivalently across the registered harnesses. Record a reason for every inclusion/exclusion before calibration. If two servers duplicate the same capability, choose and freeze one unless both have a stated purpose. Adding a server after scored dispatch changes the treatment.

## Context MCP documentation corpus

Use the installed **Context MCP (`@neuledge/context`)**, currently named `library-docs`, as the first documentation adapter to qualify. This name identifies the observed package; it does not assume Context7 or another similarly named service.

1. After the baseline stack is selected, derive required documentation from actual runtime/dependency versions: UI framework and React, TypeScript, HTTP/API framework, local database/driver and migration tooling, authentication if present, test runner, and browser test tooling. Include the relevant repository instructions and public API/schema references. Do not carry the development box's existing Next/Auth/Vitest/Python selections into the study by default.
2. Prefer official version-local documentation. Record package/library ID, exact version, original source URL, retrieval date, license, archive hash and extraction/index hash. Community-built Context packages require source/version/coverage review; a version label alone is insufficient. Missing or mismatched coverage is resolved before freezing.
3. Prefetch the approved packages outside subject timing. Context's installed README documents `context serve --libs name@version ...`; use exact versions, not bare names. In this mode its registry search and package-download tools are hidden. Verify that behavior through actual `tools/list` and requests in the installed version. Freeze the complete argument list after the stack is known.
4. Package approved custom/local docs through the qualified adapter. If local RAG is needed, expose the same frozen source documents and record chunking, embedding/reranking model, inference route, index format, seeds where supported and output limits. Retrieval model calls must be fixed, disclosed and measured separately from subject usage; disable unregistered generative answers or model delegation.
5. Mount the source corpus read-only. Keep each process's writable cache/index state independent, or distribute an immutable prebuilt index with private writable overlays. Exclude other repositories, prior solutions, sealed checks, reference implementations, controller logs and other runs. Do not reuse global search indexes.
6. Disable live registry updates, unapproved downloads and general web access during runs. If enforced offline serving is unavailable, prefetch and enforce a network allowlist/deny policy outside the subject. Confirm docs remain available with external access blocked. Preserve a read-only file copy of the same corpus for every arm.
7. Test a frozen query set: version-specific API lookup, relevant example retrieval, source attribution, no-result behavior, wrong-version request and attempted access outside the corpus. Check relevant evidence can be retrieved consistently; exact prose/ranking equality is only required if the backend promises determinism. Freeze result limits and query fixtures.

Document which library versions have no approved docs and any remaining coverage gaps. Subjects receive the same corpus manifest and usage instructions; retrieval choices remain part of their agent behavior.

## Common configuration and isolation

- Pin server package/runtime versions and executable/container digests. Use per-study configuration rather than importing the machine's global MCP catalog. Sanitize launch manifests; keep credential values outside logs and the public repository.
- Register the same tool inventory, tool schemas, descriptions, timeout/retry limits, startup policy, result truncation and permissions for every arm. Keep native tool overlap and adapter differences visible. When a capability cannot be equivalent, resolve it before freezing or explicitly revise the systems being compared.
- Expose the same bundle to both supervisors and every worker session through the fixed worker broker. No persistent worker may retain another run's index, conversation or cached results.
- Scope browser navigation to the disposable local app. Preserve independent evaluator/browser state. Register allowed interactions for supervisors under the existing rule that Gemma performs all application/test edits.
- Scope navigation/index servers to the current baseline and allowed working tree. Verify new-file/change visibility, index refresh policy, sibling-path rejection and task-only history. MCP tools must not expand a role's edit permissions or access to evaluator artifacts.
- Deny unrelated global servers and skills. Explicitly test resolved configuration, not just configuration files. Assert both process working directory and inherited `PWD` match the run directory, following the Terra readiness launcher finding.

## Qualification and launch gates

1. **Inventory:** capture server versions, launchers, dependencies, licenses, network/filesystem needs, tool catalogs and current health. Select the common bundle and record inclusion decisions.
2. **Configure:** create isolated server manifests and both harness adapters. Prepare the frozen Context corpus and any task-specific baseline indexes before timing.
3. **Smoke:** exercise initialize, tool listing, a real call and shutdown in each direct/supervisor/worker role. Test timeout, crash, unavailable docs, forbidden path and network denial. Inspect logs for unexpected models, downloads, repositories or credentials.
4. **Parity:** compare effective tool schemas and corpus hashes across adapters. Demonstrate the fixed worker broker passes the same configuration. Retain unsupported differences and their resolutions.
5. **Measure:** log request/session IDs, UTC and monotonic timestamps, tool name, status, latency, retries, output truncation and corpus/index revision. Keep tool arguments/results private if they expose task content. Freeze a cold-start/warm-up policy: prestart and health-check before dispatch for all arms; ordinary retrieval and refresh latency after dispatch counts toward the workflow deadline. Record setup/indexing overhead separately.
6. **Freeze:** commit sanitized manifests, source hashes, qualification results, role/tool matrix and exclusions; store raw evidence privately. Sign the MCP gate before calibration and carry the same bundle into scoring. A calibration-driven change requires a versioned amendment and requalification of affected calibration runs.

Server failure uses the registered timeout/retry policy. The controller records mechanical recovery without product hints or adaptive tool substitution. Infrastructure interruptions follow the protocol's endpoint/missingness rules. Every arm has the same documented file-based access to the frozen corpus, but switching adapters or adding documents mid-study requires a registered amendment.

## Required artifacts

- `mcp/inventory.json`: discovered versions, availability, capability and inclusion decision.
- `mcp/manifest.json`: pinned launch definitions, per-role tool/permission matrix, adapter versions, timeouts/retries and network/mount rules.
- `docs/corpus-manifest.json`: source/version/license/provenance hashes and index/retrieval settings.
- `mcp/qualification.json`: startup, tool-call, role parity, offline retrieval and isolation evidence; unresolved gaps and signoffs.
- Private MCP event logs with sanitized timing/call summaries for publication.

These are planned artifacts, not files already qualified. The registration retains null evidence hashes until setup is performed. Existing documentation-server installations were built for other projects and must be scoped anew.
