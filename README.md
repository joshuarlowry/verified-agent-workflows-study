# Verified Agent Workflows — Study 2

**Draft revision 2. No experiments have started.**

## Hypothesis and decision

**Can Gemma with a strong supervisor deliver nearly as reliably as Terra alone for substantially less money?** We expect supervision may improve Gemma enough to make this tradeoff useful; the previous pilot did not establish it.

The proposed target is **within 10 percentage points of Terra's completion rate, at no more than half its standardized model cost per accepted result**. Both conditions must hold. Favorable point estimates mean “promising, inconclusive”; sufficiently precise bounds and independent review could support a separate deployment validation. Completion is a gate, not a weighted score.

## Configurations

| System | Implements | Plans/reviews |
|---|---|---|
| Gemma alone | Gemma | Gemma |
| GLM alone | GLM | GLM |
| Terra alone | Terra/Codex | Terra/Codex |
| Terra supervising Gemma | Gemma | Terra/Codex |
| GLM supervising Gemma | Gemma | GLM/OpenCode |

The exact three model IDs are retained. These compare **whole systems**, including harnesses. Terra stays in Codex.

**Transport update:** [Terra through OpenRouter passed a separate readiness check](readiness/terra-openrouter-20261107.md), including OpenCode tool use. This makes a common OpenCode harness feasible to consider; it does not change the draft configurations above or constitute a study run.

## Workload and limits

Use a new small application with real UI, API and a disposable local database.

- **Calibration:** four tasks × five systems × two repetitions = 40 unscored runs, beginning with a ten-run smoke pilot included in that total.
- **Core:** fifteen tasks × five systems × two repetitions = 150 scored runs.
- **Retry control:** fifteen extra Gemma runs enable public-check-selected best-of-three: **165 scored generations total**. All three candidates incur cost; the portfolio has up to three times the core deadline.
- **Deadline:** five times accepted calibration median runtime, bounded between 30 and 120 minutes, then frozen uniformly. Calibration has a 120-minute cap. No dollar/token cap.

Qualify five scored tasks first, collect 55 runs, then apply an outcome-blinded feasibility checkpoint before the remaining ten. Freeze all contracts/order upfront; rankings cannot steer later construction.

## Outcomes and analysis

The two primary comparisons are each supervised Gemma system versus Terra alone. Measure verified completion, cost per acceptance including failures, delivery time and timed blinded **“would I merge this?” review**.

Primary economics use frozen **uncached API-equivalent prices**, not subscription invoices. Actual bills, cache discounts and subscription allocations remain separate scenarios. Public checks are examples; sealed checks cover new cases of disclosed requirements.

Analyze matched task clusters. Calibration informs precision simulations; fifteen tasks may not establish a ten-point margin. Inconclusive is valid. All other comparisons are secondary.

## Next step and documents

Appoint independent fixture builders and reviewers. Subject models **and their families** are excluded from building the app, reference solutions and acceptance checks. This AI coordinator drafted the plan; that does not qualify it to construct the benchmark.

[Protocol](PROTOCOL.md) · [Analysis plan](ANALYSIS_PLAN.md) · [Task template](TASK_TEMPLATE.md) · [Registration](registration.json) · [Revision notes](CHANGELOG.md)

This is the public planning record following the [Minutes pilot](https://joshuarlowry.github.io/minutes-agent-workflow-study/). AI roles are disclosed; sealed tests, credentials and unreleased solutions remain private. Registration is incomplete and not launchable.
