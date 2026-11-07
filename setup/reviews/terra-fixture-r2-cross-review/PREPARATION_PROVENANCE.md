# R2 cross-review provenance

## Identity and limits

This is a fresh disclosed review of GLM's R2 fixture, not authorship of task solutions, independent-family replication, qualification, calibration or scoring. The request identifies Terra as `openai/gpt-6.1-terra` on Azure with high reasoning. The observable harness identifies this session as **Terra Azure High**, `study2-terra-fixture-review/terra`; exact resolved upstream revision and route are not independently established. GLM authored the baseline and repairs; Terra is a different study subject family, not independent-family evidence. No other model or subagent was invoked. Gemma, GLM and Terra were the authorized families.

Controller session identity and time records are the authority for provenance; they were not provided in the supplied inputs. No invented session timestamp or upstream route is asserted. The controller-exposed execution environment reports 2026-11-07; actual shell `date -u '+%Y-%m-%dT%H:%M:%SZ'` returned `2026-11-07T05:10:54Z` near start and `2026-11-07T05:15:01Z` during review. These shell clock observations are not a replacement for controller evidence. Node `v24.19.0`, npm `10.9.0`; Playwright reported an unsupported host and downloaded its Ubuntu 24.04 fallback. Host OS identity was not independently established.

## Immutable source identity

- `/workspace/inputs/endpoint-manifest.json`: SHA-256 `663347850176614ed0ec0c362a94ee840c91521fb818305eb525cca3d298759e`.
- `/workspace/inputs/prior-review.json`: SHA-256 `0a92d4dc8cb108efc2395f7e10793cd1c302f14685f5a81f33c7d686fb2b2e9c`.
- Outer canonical array tree SHA-256 `71cef603e46ef3a424cf86610c16394ea2e72a5ad4f5d6b73e47ac192d79488b`; 74 distinct regular files, each path, size and hash verified; no unlisted files. Full per-file exact hashes are retained in `/workspace/diagnostics/source-hashes-after.txt` and the input manifest, not merely referenced without verification.
- Independently computed tree SHA-256 `608d7ba5494ae1bee23e1cb6b50468b8a559f9eabdde73dd2bdd60101564e257`, sorted relative UTF-8 path + NUL + lowercase ASCII SHA-256 + LF. Inner `r2-endpoint-manifest.json` lists 73 matching files with canonical tree `51f627395573b4774b7e7c57894ca00780275b6337045b1d13c757b1ef59e99f`; outer adds that manifest itself.
- Before/after verification and comparison exit 0. Inputs were not edited. The R1 source and its manifest are not supplied, so historical pre-edit comparisons in GLM's record are not independently reconstructed.

## Review method and retained evidence

Read actual application, test, baseline contract, R2 dispositions, FAQ, calibration and scored contracts. Ran the public full check on a fresh copy before adding diagnostic code. Read source/tests and ran non-authoritative scoped browser, route, SQLite and static census diagnostics, all under `/workspace/diagnostics`. Exact commands, working directories, exit codes and findings are in `/workspace/FIXTURE_R2_CROSS_REVIEW.json`. Logs include `check-full.log`, `scope-diagnostic.log`, `routes.log`, `keyset.log`, `census.log`, `seed-validation.log`, `browser-install.log` and the before/after hash lists. The review-authored probes are **diagnostics, not acceptance fixtures or replacement implementations**. The copied scratch baseline and disposable local SQLite files are not the input fixture.

Fresh installation and `check:full` returned 0: typecheck, lint, 11 unit, 36 API, 20 Playwright tests; Better Auth emitted expected initial schema warnings. A passing public check is not proof of scope/race safety or contract consistency. Scope diagnostic exit 0 means it successfully asserted two **unwanted** behaviors. Key diagnostic hashes:

- `scratch-baseline/e2e/diagnostic-r2-scope.spec.ts`: `1425eafb3fb4a8ed422570f84a7f0ab725be9c981c125b7604d73601ba4df2ee`.
- `scratch-baseline/diagnostic-routes.mts`: `1fa831e337eff287da0509fd543fd09800e44a79897fe45887e5cf627faabbf1`.
- `scratch-baseline/diagnostic-keyset.mts`: `31c12e09753d35154aad10cdf0d8e6828d125ca49086fa79a5db0b763c7222c6`.
- `scratch-baseline/diagnostic-seed-validation.mts`: `2f7173b7f98008589047622cb3f112bb887cc02d28a1fdd5f33081e59677c0a5`.
- `census.py`: `35db51b99320d4f2fe9617dda16e86c2e5fb66d3e46de63de036186d4fb6e3b1`.
- `check-full.log`: `5ab821044e6c5538e50f5bb2a8ec927953a34a0bd92284f5b276dec75ce957ee`.

## Decision and gates

Changes are required: the baseline violates its new cross-scope action rule and overgeneralizes Better Auth HEAD status; C1's exhaustive migration misses calls; S03's nondecreasing-clock guarantee fails on future seed keys; S10's dirty guard conflicts with the newly added held-create regression. The root README still asserts an absent current `review-inputs/` mount. Full evidence, precise scope, all R1-N1–N9 dispositions and C1–C4/S01–S15 contract verdicts are in the JSON report.

Baseline and C1 are not consistent enough to freeze. C2–C4 are sufficiently coherent drafts for construction planning after the shared baseline blocker is resolved, not qualified or validated; defects specific to S03/S10 do not automatically preclude those calibrations. Do not require nonexistent task implementations merely to judge draft consistency. Every scored contract remains unfrozen: core inspection does not establish comprehensive consistency, security or testability. Before calibration, authorized reference/alternate/evaluator construction, hidden controls, independent review and clean-instance qualification remain required. Packaging, sources/licensing/context, controller route/timing/usage, scoring and outside-scope U1–U3 remain separate gates.

Stop point: review only. No input edits, product fixes, replacement solutions, reference/evaluator creation, calibration or scored runs; no account/budget/production changes, deployments, pushes, merges, worker calls or study dispatch. Intentional task gaps and switch-time unguarded discard remain intact.
