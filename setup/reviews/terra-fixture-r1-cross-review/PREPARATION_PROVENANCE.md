# Preparation provenance — R1 cross-review

## Scope and identity

This is a fresh-session **preparation cross-review** of the GLM R1 repair,
not a task attempt, calibration, scored run, reference implementation,
sealed evaluation, qualification, or production approval. The user authorized
only Gemma, GLM and Terra; this session invoked **no subagents or other
models**.

The requested reviewer was Terra `openai/gpt-6.1-terra`, Azure, high
reasoning. The harness identifies this session as
`study2-terra-fixture-review/terra`, Terra Azure High. I did not observe an
independently resolved upstream provider revision or full routing chain; those
are not inferred. No review timestamp is claimed here: controller evidence
supplements identity and time. GLM authored the fixture and R1 repair. Terra
reviewed it in this separate session; the participating subject-model
families are part of the study, so this is **subject-family-dependent
cross-review, not independent-family authorship or replication**.

## Inputs and exact endpoint

- `inputs/endpoint-manifest.json`: SHA-256
  `8221af9577f0de58a209f4c8bc3041384738a18d162c2742c7671a74e5156e72`.
- `inputs/prior-review.json`: SHA-256
  `594bf8fb1a7e45696c6b777bc086f9d1220ea092e70e0e208ba2e9c3861082fd`.
- R1 manifest array SHA-256, independently recomputed using its specified
  compact sorted-key JSON encoding:
  `35f22c5abce72cdc9956d428ab40ceefe9d42e285402ef34c686f1a016eb4b6b`.
- Independent fixture tree SHA-256 using sorted path + NUL + file hash + LF:
  `00143dd91ccf0aec27c202e8058c74575aa97fcb5483eae8eef7e7112b58d6c4`.

All **71** listed source paths, byte lengths and individual hashes matched;
there were no extra or missing regular files. The full exact per-file hashes
are in the verified manifest. I repeated the source-file and input-hash check
after the diagnostics. Source inputs were not changed. The previous endpoint's
source and manifest are not present, so GLM's pre-edit identity comparison is
historical evidence rather than an independently repeated byte comparison.

## Work and diagnostic boundary

I inspected the original findings B1–B3, C1–C2, S1–S6, A1 and D1 against
R1's dispositions, baseline, tests, FAQ and all 19 task contracts. U1–U3
concern other files and are outside this review. I checked seed counts and
ordering via a SQLite scratch diagnostic, direct dependency pins against the
lockfile, and the installed SQLite version.

I copied only `inputs/fixture/baseline` to the explicitly disposable
`/tmp/opencode/workboard-r1-review-scratch`, installed from the lockfile, and
installed the pinned Playwright headless shell in the private cache
`/tmp/opencode/workboard-r1-review-browsers`. The unmodified scratch source
passed the public full check: typecheck, lint, 11 unit, 34 API and 18 browser
tests. Playwright reported an unsupported host and selected an Ubuntu 24.04
fallback build. A foreign listener caused Playwright to fail rather than reuse
it. A separate empty-home test reproduced the missing-cache failure when a
relocated browser installation is not accompanied by the same environment
variable at execution.

After the clean full check, I added **review-only, non-authoritative**
diagnostics in scratch. They exercised stale list/actions under delayed and
failed switching, a late mutation completion across a workspace switch, route
precedence, seed sorting, and a same-timestamp keyset counterexample. Their
paths, exact SHA-256 values, commands, exit codes and interpretations are in
`FIXTURE_R1_CROSS_REVIEW.json`. A diagnostic test passing while asserting a
bug is not a passing safety verdict. Generated dependencies, browser cache,
builds, disposable test databases and artifacts are not source inputs. No
application or test fixes and no replacement task solutions were supplied.

## Outcome and stop point

The review verdict is **changes required**. The original delayed/failed
stale-list defect is repaired and meaningfully regression-tested, but an
in-flight create completion still affects a newly selected workspace's UI.
The machine report details additional concrete API-wording, test-migration,
calendar, keyset and import/draft-contract defects with reproductions.

The task defaults are experimental, not production decisions. Reference
solutions, sealed tests and oracles are separate future qualification gates;
their absence alone does not prevent an internally consistent draft verdict.
No calibration, scoring, provider usage/broker qualification, Context archive
qualification, or model-favoring task selection was performed. This session
stops at the cross-review endpoint.
