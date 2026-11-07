# PREPARATION_PROVENANCE.md — GLM docs corpus cross-review (first endpoint)

- Reviewer: GLM (z-ai/glm-5.3-flash, provider_tag relace/fp4, OpenCode -> LiteLLM -> OpenRouter), fresh session, no builder conversation imported. This is study-model cross-review, **not** independent-family qualification (registration.json `qualifier_label`).
- Review window: 2026-11-07, started ~04:43 UTC (self-reported; controller measurements will supersede).
- Review endpoint reached; no app/tests written, no inputs mutated, no calibration started, no deploy/push.

## Inputs received and their SHA-256

| Input | SHA-256 |
| --- | --- |
| registration.json | e46d5a308b93b839d3b50e0c1e4d675294b6c22069c91017e6b99cbe6f65410b |
| source-inventory.json | d130b1c57a1df8c7c28723ab20f83338c6d8b84c4adbecbb927531ae225fa5fe |
| application-package-lock.json | 2fa59272fde383011374d769e06b419946b197aedf42887b7d6860faee471246 |
| context-mechanical-probe.py | d7750f044b8a25f8985d7e8e41d41d8e0af00a30f111fee1e0754b793e2392b5 |
| corpus/CORPUS_BUILD_PROVENANCE.md | a9f20ba1d9ddff63867095a3bf4785d4baeace2d8de809c5b0e57c447606ebf0 |
| corpus/CORPUS_MANIFEST.json | b67c1094e05dc4693d1306ff9b97624acef20d514dd54e224f77618eb9956d18 |
| corpus/corpus_plan.json | e980b806a773703d9a94ee1e63392d63f93903a5d928fa435acf91e5e84c6ba8 |
| corpus/all_hashes.txt | f3042870027978a97db13e0825ce22b97acdbfe637235ec3999a45ba3f26df78 |
| corpus/hashes_text.txt | c5e142ae4cd3955e3791b0bb0a93dd1c8425b45b1d162cb5e6ac6831b917323a |
| corpus/hashes_pkgs.txt | 5b9787c04d8f5dd6a07629e09a389e8fd988923c484513f460487ac9a84650cd |
| corpus/manifest_temp.txt | 2e3b85b65fc0b14aeed665aa93113b4db227e30b2e96988c9b00e531ed8a6f56 |
| 21 corpus artifacts (9 text + 12 .db) | verified via `sha256sum -c hashes_text.txt && sha256sum -c hashes_pkgs.txt` → all OK, exit 0 |

## What was verified (with reproductions; full transcript in diagnostics/repro_transcript.md)

1. **Hashes/counts.** All 21 artifacts verify against the hash lists. The manifest's 9 text hashes match. One manifest archive hash is malformed: `context-packages/vitejs_plugin_react@6.2.1.db` is recorded as a 65-character hash (extra `8` at position 43); the actual file hash `d6c833f82eb373e2532be2535b14c38522c09e3e7f5bdbb0d34a289fc55a1d64` matches `hashes_pkgs.txt` and `all_hashes.txt`. `package_count: 13` ≠ 12 archives/12 mapping entries. Manifest timestamp `2026-11-07T12:00:00Z` is ~7 h after the real artifact mtimes (04:32–04:41 UTC) — placeholder.
2. **Scoped serve mechanics (Context 1.3.3, `/tools/context/node_modules`).** Copied the 12 `.db` files into a fresh private `~/.context/packages` (copies byte-identical, re-hashed). `serve --libs <12 exact name@version>` in stdio MCP mode: `tools/list == ["get_docs"]` (registry search/download hidden), `get_docs` accepts exactly the 12 approved name@version strings, `unlisted-library@0.0.1` and bare `vite` are rejected (MCP -32602), and all 12 libraries return nonempty results for representative topics. Unscoped serve exposes `search_packages`/`download_package`, confirming what scoping hides. Evidence: `diagnostics/serve_scoping_probe_result.json`.
3. **Two-way content comparison.** Verbatim live-source matches for vite (live site header shows **v8.3.6**), react (reference ToC), better-auth (**1.7.x** llms.txt, live), better-sqlite3 (current api.md), eslint landing, playwright intro. Stubs spot-checked accurate (MDN writeText NotAllowedError/secure-context; WAL persistence; Node latest-v24.x = **24.22.2**). FTS indexes complete in all 12 DBs (235 chunks, 0 missing; `context list` counts match).
4. **Pins/licenses/peers.** All 18 pinned versions exist on npm; licenses match the inventory (MIT; typescript and @playwright/test Apache-2.0); peer ranges verified (@vitejs/plugin-react→vite ^8.0.0; vitest→vite ^6.4.0||^7||^8; typescript-eslint and eslint-plugin-react-hooks→eslint ^10.0.0; @hono/node-server→hono ^4). Lockfile root is exactly pinned with `engines.node = 24.19.0`; this review environment independently runs node v24.19.0 / npm 10.9.0.
5. **SQLite claim reproduced.** Fresh `npm install better-sqlite3@13.0.3` on Node 24.19.0 → `SELECT sqlite_version()` = **3.53.4** (matches source-inventory). Note: sqlite.org/wal.html (retrieved; last updated 2026-08-25) documents the WAL-reset bug present through 3.51.2 and fixed in 3.51.3 — the bundled 3.53.4 is past the fix; the corpus never mentions it.
6. **Task-specific hints.** Scanned all 235 chunk contents and 9 stubs for workboard/`WORKBOARD_`/task/contract/acceptance/fixture/`C[0-9]`/`S[0-9]` patterns: no matches. No task contracts or solutions exist in this endpoint and none were used.

## Why changes_required (construction defects)

1. Malformed manifest hash (above) — manifest self-integrity fails.
2. `eslint_toolchain@exact.db`: version label **"exact"** is not a version (violates `exact_version_allowlist_required`); content is only the typescript-eslint quickstart — no @eslint/js, eslint-plugin-react-hooks, or globals content for the 4 bundled packages.
3. Provenance misdescription: the 9 `docs-files/text/*` files are called "raw Markdown snapshots fetched via webfetch"; they are 196–410-byte self-authored summaries. Factual spot-checks pass, but the extraction claim is false as written.
4. The provenance serve command (`serve --libs vite react hono better_auth better_sqlite3 vitest playwright eslint tsx`) restricts to **9** packages — silently omitting `vitejs_plugin_react@6.2.1`, `hono_node_server@2.1.6`, `eslint_toolchain@exact` — and uses bare names rather than the registered exact name@version form ("Restricted to 9 packages" captured in `diagnostics/provenance_serve_command_check.txt`).
5. `corpus_plan.json` plans 14 package text files (`docs-files/text/vite.md`, `react_react_dom.md`, …) — none exist; the plan was never reconciled with the manifest.
6. **react-dom is missing with no declared gap** (no archive; no text file; `query react@19.3.1 createRoot` → 0 results).
7. `manifest_temp.txt` is an unexplained stdin-hash leftover matching nothing in the endpoint.
8. Provenance references `inputs/baseline/package.json`, which is not present in this endpoint's inputs.

## Declared preparation gaps (honest, not defects)

- TypeScript extraction failed; @types/better-sqlite3 extraction failed (both declared in provenance).
- Node 24.19.0 vs latest-24.x (24.22.2) docs drift (declared).
- System-doc licenses "Not verified" (declared) — **redistribution terms remain unverified**.

## Undeclared coverage gaps found by this review

- ToC/index-only archives for react, hono, better-auth, playwright, vitest, eslint: the source-inventory's own declared relevant_topics (createRoot; app.request/routing/onError; emailAndPassword/sqlite-instance/auth.handler/migrations; webServer/getByRole/strict mode/serial/route interception; pool/environment/timeout; flat config/no-useless-assignment/exit codes) return **empty** or tangential results (recorded in `diagnostics/`).
- No attribution/LICENSE evidence ships with any archive; package licenses are verified but publication terms are not.
- Stale state: source-inventory `context_archives: "NOT BUILT"` and registration `coverage_gaps: "Vite/Hono ... not yet built"` contradict the built corpus.

## What can be published now

**Nothing.** Redistribution terms are unverified for every source (system docs declared "Not verified"; archives ship no attribution), and the manifest/provenance defects above must be repaired first. The hash-verified artifacts can continue as internal preparation/review material; they are not approved for publication.

## Minimal actionable repair list

1. Regenerate `CORPUS_MANIFEST.json` (fix the 65-char hash, true counts, real timestamp; drop `manifest_temp.txt`).
2. Rewrite `CORPUS_BUILD_PROVENANCE.md` (summaries not snapshots; declare react-dom + missing package text files; exact 12-name@version serve command; fix the baseline path reference).
3. Replace `eslint_toolchain@exact.db` with real per-version archives or embed component versions + react-hooks content.
4. Build substantive content for react/react-dom, hono, better-auth, playwright, vitest, eslint archives (or amend `relevant_topics` to actual coverage).
5. Capture per-source license/attribution evidence before any publication.
6. Revise stale `source-inventory.json` / registration entries after rebuild; re-run the scoped-serve probe.

## Reviewer self-authorship statement

`/workspace/DOCS_CROSS_REVIEW.json`, this file, and `/workspace/diagnostics/*` (serve probe + result JSON, chunk dump, repro transcript, hash/peer/registry check outputs, sqlite-version check, db copies, provenance-command check) are self-authored review artifacts from this session. They are **unapproved** and are not final acceptance; per registration `artifact_policies` they require coordinator handling and another-authorized-model review before any freeze decision. No verification beyond what is recorded here should be attributed to this review.

Stop: review endpoint reached.
