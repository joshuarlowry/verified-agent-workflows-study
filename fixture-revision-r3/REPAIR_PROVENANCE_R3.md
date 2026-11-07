# Repair provenance — R3 construction endpoint

## Identity, scope and disclosure

This is a separate preparation construction revision, not a scored rescue,
qualification, calibration, or task attempt. The harness identifies this
session as **Terra Azure High**, `study2-terra-fixture-review/terra`; the
requested route was `openai/gpt-6.1-terra` via OpenCode/LiteLLM/OpenRouter/Azure,
high reasoning. The exact upstream model revision, route and session timing
are not independently resolved here; controller records are authoritative.
No other model or subagent was invoked. GLM authored the preserved prior
baseline and R1/R2 repairs; Terra authored R3. Both are authorized study
subject families, so authorship and subsequent review are not independent-
family evidence. A fresh GLM cross-review of R3 is required after this
endpoint. Self-review below is not approval or a substitute for that review.

No task features, reference implementations, hidden evaluator or calibration
were constructed; no production DB, account/budget change, deployment, push,
merge, or study dispatch. Package pins are unchanged. Tests use disposable
local SQLite; npm and Playwright package downloads were used for construction.
Historical provenance/reports were not rewritten.

## Input identity

`outputs/r3/verify_prior.py` verified all 74 unique outer-manifest entries,
bytes and hashes before editing. Canonical array SHA-256 was
`71cef603e46ef3a424cf86610c16394ea2e72a5ad4f5d6b73e47ac192d79488b`;
independent path/NUL/hash/LF digest was
`608d7ba5494ae1bee23e1cb6b50468b8a559f9eabdde73dd2bdd60101564e257`.
The outer manifest hash matched the immutable R2 review's
`663347850176614ed0ec0c362a94ee840c91521fb818305eb525cca3d298759e`.
`outputs/r3/audit-static-final.log` also verifies the 73-entry inner manifest
canonical digest and every inner entry against the verified outer list.
The original R1 tree/manifest is not supplied and was not reconstructed.
`outputs/r3/input-hashes.txt` records the supplied review and manifests; their
post-edit `sha256sum -c` matched. `outputs/r3/source-diff.log` confirms the
historical records and package pins unchanged. The inputs are excluded from
R3 source manifest as external evidence, not deleted.

## Choices and dispositions

The machine-readable `REPAIR_DISPOSITIONS_R3.json` gives finding-by-finding
evidence and limitations. Key choices:

- Synchronous selection generation avoids effect-lag and ABA; form generation
  invalidates replaced/closed forms and delete generation invalidates replaced
  confirmations or overlapping deletes. Delete completion also checks form
  generation, so a newer same-selection form receives no stale feedback or
  reload. The success caller closes edit only
  inside its guarded completion. Form catch, field errors, and finally use the
  same token; switch-time draft discard remains deliberately unguarded.
  Successful server writes persist, but stale completions do not trigger a
  reload; a later selection or other normal reload retrieves them.
- Tests hold actual successful responses after `route.fetch`, synthesize
  failures without a server write, and wait for both delivery and application
  response-body consumption followed by task/microtask and React frame turns.
  For 204 the wrapper marks consumption when fetch resolves. They assert new
  drafts, pending flags, confirmation, feedback, and persisted results. Tests
  clean their own diagnostic rows. The barrier instruments test pages only;
  it is not a production feature or sleep-only negative assertion.
- C1 explicitly permits workspace label-to-stable-value selection migrations
  in named files, with seed option-text assertions retained. This handles
  dynamic counts without hard-coded values. S10 retains the dirty guard while
  pending and authorizes narrow equivalent-coverage flow migrations.
- S03 chooses live keyset semantics: nondecreasing clock does not remove
  future-stored-key repeats. Example top-position precondition compares the
  observed PATCH timestamp with the pre-PATCH maximum, not just the cursor.
  No live clock or seed rewrite was assumed. HEAD documentation follows
  observed handler behavior without altering authentication.

## Commands and results

Paths/logs below are under `/workspace/outputs/r3/`; commands run from
`/workspace/baseline` unless specified. Output was redirected directly, not
piped through a process that masks exit codes.

| Command | Exit | Evidence |
|---|---:|---|
| `python3 outputs/r3/verify_prior.py` from `/workspace` | 0 | `prior-verification.log`; outer hashes and independent digest matched. The invocation used `tee`; script was also inspected for explicit failure conditions; no mismatches printed. |
| `npm ci --no-audit --no-fund` | 0 | `npm-ci.log`; Node v24.19.0/npm 10.9.0 |
| `PLAYWRIGHT_BROWSERS_PATH=/workspace/outputs/r3/browsers npx playwright install chromium --only-shell` | 0 | `browser-install.log`; unsupported OS warning and Ubuntu 24.04 **fallback label**, not a host OS identification |
| `CI=1 PLAYWRIGHT_BROWSERS_PATH=/workspace/outputs/r3/browsers npx playwright test e2e/isolation.spec.ts` before app fix | 1 | `diagnostic-red.log`: edit success and ABA create lost later forms; also two diagnostic mistakes described below |
| same isolation command after first fix | 0 | `isolation-first-fix.log`: 8 passed |
| `npm run typecheck` | 2 then 0 | `typecheck-initial.log`, `typecheck-after.log`: missing DOM types in test helper and unused type fixed |
| `CI=1 PLAYWRIGHT_BROWSERS_PATH=/workspace/outputs/r3/browsers npm run check:full` interim | 0 | `check-first.log`: 11 unit, 36 API, 31 e2e |
| same isolation command after ABA expansion | 0 | `isolation-expanded.log`: 17 passed |
| in `outputs/r3/mutant`: `CI=1 PLAYWRIGHT_BROWSERS_PATH=/workspace/outputs/r3/browsers npx playwright test e2e/isolation.spec.ts --grep 'held edit success|ABA create success|old delete failure'` | 1 expected | `mutant-check-retry.log`: deliberately disabled scope tokens; all three selected regressions fail after processing barrier. Source and script retained outside app. |
| `CI=1 PLAYWRIGHT_BROWSERS_PATH=/workspace/outputs/r3/browsers npm run check:full` | 0 | `check-final.log`: typecheck/lint, 11 unit, 36 API, 39 e2e; before the final same-selection delete/form refinement. |
| same full command after final code/test edits | **0** | `check-final-rerun.log`: typecheck and lint pass, **11 unit, 36 API, 41 e2e**; build runs via e2e server. Better Auth prints known initialization schema warnings before setup and invalid-password warning. |
| `python3 outputs/r3/audit_static.py` and `python3 outputs/r3/compare_sources.py` from `/workspace` | 0 | static census, inner manifest, pins and unchanged historical files |
| `sha256sum -c outputs/r3/input-hashes.txt` from `/workspace` | 0 | supplied review and manifests unchanged |
| `python3 outputs/r3/verify_prior.py` after edits | 1 expected | `post-edit-prior-check.log` reports changed source paths; it is a pre-edit identity checker, not an endpoint verification |

First diagnostic failures were investigated rather than treated as app bugs:
edit-failure's unscoped text assertion matched a preceding test's row; it was
scoped to its target card. Calling `page.unroute` while the old route was
held let that request escape and caused the pending-form test timeout; the
second route is now registered without unroute. Initial mutant command used
unsupported `--expect-timeout=1000` and exited 1 before running tests; rerun
without that flag produced the actual three expected failures. Typecheck's
missing browser ambient types and unused type were fixed without changing
compiler/package configuration. Logs retain the failures.

## Self-review and limits

Reviewed every mutation completion/caller and reset path, including response
success/failure, ABA, form replacement and delete replacement. This audit
identified that a same-selection delete completion could still announce or
reload after a new form opened; guarded it by form generation and added two
success/failure regressions before the final full run. Confirmed
selection tokens advance synchronously and stale catch/finally do not affect
a newer form. Examined the public test selection census and API assertions;
new tests use stable workspace values. Reconciled FAQ, baseline HTTP contract,
S03 examples/acceptance, S10 guard migrations and root mount description.
The mutant check proves selected guards are actually observed, not that all
possible races are exhausted. Tests use a response-consumption + scheduling
barrier tied to the current React implementation, not a formal event-loop
proof; unusual browser scheduling, network failures and multi-click overlaps
remain qualification scope. S10 and C1 migrations and S03 controlled-clock
examples are contract choices, not implemented task solutions; they have not
been demonstrated against a reference implementation. Other draft contracts
retain the R2 review's qualification limitations and need separate review.
Better Auth edge methods beyond recorded cases, clipboard/browser portability,
legacy dates, mixed-error precedence and full concurrency remain unqualified.

R3 source hashes are generated programmatically in `r3-endpoint-manifest.json`
(excluding the manifest itself, external inputs, outputs and generated app
artifacts). The final full check ran after all application and test edits.
Stop here: no self cross-review approval; fresh GLM review remains required.
