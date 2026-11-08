# C1 calibration: first verified results

Published Nov 08, 2026 at 08:56 AM EST. AI-managed study; all original endpoints remain preserved.

**5 of 10 runs passed every frozen machine gate.** This is one calibration task, with two repetitions per workflow. No scored study runs have started.

All five systems use OpenCode → LiteLLM → OpenRouter. The pinned Gemma route serves BF16; the pinned GLM route serves FP4; Terra uses Azure with high reasoning. Exact dated model IDs and settings remain in [registration.json](../registration.json).

| Workflow | Trial | Frozen result | Runtime | Recorded charges |
|---|---:|---|---:|---:|
| GLM supervising Gemma | 1 | Pass: all frozen gates | 3m 57s | ≥ $0.0529 |
| GLM alone | 1 | Pass: all frozen gates | 4m 32s | $0.0538 |
| Terra alone | 1 | Reject: test-preservation policy only | 2m 45s | $0.1393 |
| Gemma alone | 1 | Fail: feature acceptance | 9m 43s | ≥ $0.1157 |
| Terra supervising Gemma | 1 | No delivery: infrastructure interruption | 49m 04s | ≥ $0.9536 |
| Terra alone | 2 | Reject: test-preservation policy only | 3m 40s | $0.1888 |
| Terra supervising Gemma | 2 | No delivery: infrastructure interruption | 1h 42m 47s | ≥ $3.8606 |
| GLM alone | 2 | Pass: all frozen gates | 4m 50s | $0.0672 |
| GLM supervising Gemma | 2 | Pass: all frozen gates | 14m 52s | ≥ $0.1600 |
| Gemma alone | 2 | Pass: all frozen gates | 11m 26s | ≥ $0.2190 |

Runtime includes tools and waits, excluding setup and between-run backups. Charges are provider-reported known subtotals; ≥ means billing is incomplete. They exclude preparation, infrastructure repair, grading and earlier technical attempts. At C1’s first publication, no standardized rate card had been frozen. Revision 21 later froze a [prospective rate card](economic-rate-card.json); any standardized C1 repricing remains post-hoc. These rows remain observed charge subtotals.

## What the checks establish

The unchanged frozen gates cover 21 public/sealed feature cases, 17 external baseline regression cases, database integrity/schema checks, 31 native authentication probes, full app checks, source/test preservation, timely final return and artifact integrity. A failing sequence can stop early: unexecuted tests are not passes.

Both direct Terra runs passed the behavioral, regression, authentication and full-app checks. Their only rejection was the finite original-test rule: new assertions were inserted inside an existing test outside the permitted locations. The original test statements were retained. This is a policy rejection, not an observed functional defect; neither primary result was upgraded after inspection. As an explicitly exploratory diagnostic, seven runs passed every gate except this source policy. That is not a replacement completion definition.

**Instrument gap:** the detailed finite test-edit grammar was absent from the public-check bundle and initial subject prompt. The public FAQ required preserved coverage without disclosing these structural exclusions. The five all-gate passes therefore cannot support a fair model-quality ranking. The mismatch must be documented and resolved prospectively, without rewriting C1 results.

Gemma trial 1 failed the first-created-workspace zero-count selector check. Both Terra-supervised attempts ended before a supervisor final: provider errors interrupted trial 1; truncated session export interrupted trial 2. Their preserved snapshots also fail lint, so later full-app checks were not executed. The capture repair was separately qualified before the last three unrun slots; no failed actor was retried.

## Provider-error attribution

A subsequent role-by-role audit of all ten fixed C1 endpoints found 440 captured response bodies identifying **Crusoe rate limits on Gemma requests**, plus seven worker-route timeout error bodies without provider metadata. No provider error body was captured on the direct GLM, direct Terra or supervisor routes. This is capture evidence, not a guarantee of platform uptime.

The first failed Terra-supervised run contains **119 Gemma/Crusoe rate-limit errors and seven worker-route timeouts**. The second contains **248 Gemma/Crusoe rate-limit errors**, in addition to the separately documented session-export endpoint failure. Those interruptions and retry delays must not be attributed solely to Terra’s coding or supervision capability. Direct Gemma and GLM-supervised runs also encountered rate limits. Workloads and retry bursts differ, so these counts are not independent reliability trials or a causal supervisor comparison. Failed-call billing remains unknown; original timings, endpoints, source and acceptance results are unchanged. [Full fixed-run/role audit and evidence hashes](c1-provider-failure-attribution.json).

## Interpretation and remaining gaps

- Acceptance is finite machine verification, not semantic completeness or human merge approval.
- The detailed finite test-edit grammar was not included in the subject public-check bundle or initial prompt. The public FAQ required preserved coverage but did not disclose these structural exclusions. This instrument/contract mismatch limits the validity of all-gate comparisons and must be resolved explicitly before later collection.
- Calibration spans disclosed harness repairs. Do not infer a model-only or uniform-harness ranking from this task.
- GLM supervisor prompts supplied detailed solution-level SQL and UI directions; Gemma made the edits. The boundary against complete replacement implementations needs explicit reporting, not a hidden new exclusion rule.
- One post-endpoint diagnostic exposed terminal worker/supervisor text to the operator; no live feedback followed. A private access disclosure is preserved.
- Mechanical operator/harness work and model preparation overhead are outside row charges. Human review effort was not measured; it is not zero.
- Earlier acknowledgement and DNS technical attempts remain additional physical attempts and overhead, outside the fixed ten nominal slots.
- Only one task is represented. No confidence intervals, cost-per-acceptance ranking or purchasing recommendation are justified here.
- The study is AI-managed. The evaluated model families also constructed and cross-reviewed benchmark materials under an explicit independence waiver; this is not an independently authored benchmark.

There are 30 remaining calibration slots before the planned 165 scored generations; their task packets still require qualification. Advancement depends on the registered integrity/readiness gates, not which workflow looks favorable here.

[Machine-readable results, role usage and evidence hashes](c1-first-results.json) · [Export-capture repair](c1-export-capture-repair-qualification.json) · [Session-export failure](c1-session-export-failure.json) · [Provider failure](c1-terra-supervised-provider-failure.json)

[Preserved application source branches and endpoint hashes](c1-source-endpoints.json). All ten nominal snapshots and the additional DNS-interrupted snapshot are published as separate branches; the study main branch is unchanged by those application commits.
