# Analysis and decision plan — draft revision 2

This document specifies the intended questions and calculations before scored data. Numeric business margins are proposed; registration must record their approval and the actual statistical-method validation. The study remains a feasibility design until its precision gate qualifies a confirmatory claim.

## 1. Two primary hypotheses

For supervised system S (Terra supervising Gemma, or GLM supervising Gemma), compared with Terra alone T:

- `Δ_S = P(accepted by deadline | S) − P(accepted by deadline | T)`.
- `K_a = total standardized model cost of arm a / number of finally accepted results in arm a`.
- `R_S = K_S / K_T`.

The working alternative is **Δ_S ≥ −0.10 and R_S ≤ 0.50**. It expresses a willingness to trade no more than ten percentage points of delivery reliability for at least half the standardized model cost per accepted result. This is a proposed business tradeoff, not a threshold inferred from the old pilot. Both components are necessary. Each null says at least one target is not met.

Only these two supervised-versus-Terra hypotheses are primary. Direct-model comparisons, supervisor-system comparisons, review/time differences and the Gemma portfolio are secondary. Report them all without using the most favorable one to replace a failed primary hypothesis.

## 2. What would change a decision?

| Result | Interpretation/action |
|---|---|
| Both target point estimates met, and uncertainty bounds support both | Candidate for a separate deployment validation, subject to readiness/review safeguards below |
| Point targets met but one or both bounds cross the threshold | Promising but inconclusive; broader independent task replication is needed |
| Valid bounds exclude at least one required target in the unfavorable direction | The proposed cost/reliability tradeoff is not supported on this task population |
| Point targets missed but uncertainty still spans them | Inconclusive, not proof that supervision cannot work |
| Zero accepted results, unresolved cost denominator, incomplete critical review or unqualified precision method | No cost/reliability decision |

Readiness safeguards: propose at least **80% observed completion** for both the candidate and Terra before recommending deployment validation; preserve every critical review defect and measure human review burden. If review burden is unresolved or review evidence shows added risk, the result is at most an economic research candidate. The 80% screen is not a lower confidence bound or a general reliability guarantee. These small-task results never directly authorize production rollout.

No midpoint of a partial-quality range substitutes for acceptance. A quick failed return provides no accepted-delivery speed advantage.

## 3. Units, pairing and missingness

A task is the sampling/uncertainty cluster. Each core system has two fresh trials per task. For task i and arm a, average its two binary acceptance indicators to obtain `p_ia`; estimate `p_a` by equally averaging tasks. Estimate Δ by averaging matched task-level differences. Preserve pairing when resampling. Never analyze 30 core trials as 30 unrelated tasks.

Primary operational accounting assigns accepted=1 only to a timely final return passing independent acceptance and critical review. Rejected, deadline, interrupted and unverified dispatched attempts are not demonstrated deliveries. Report their distinct categories; report machine eligibility separately from final acceptance.

Account-balance exhaustion stops collection globally. Unrun slots remain missing, not invented failures. Report complete-block analyses and conservative missing-outcome sensitivity bounds, including the case most unfavorable to each supervised-vs-Terra claim. No favorable decision is made from an incomplete planned sample or unresolved model/evaluator integrity. An evaluable-only acceptance rate is secondary and carries its denominator/exclusions.

All primary cost numerators include failed runs, deadline runs and paid retries, not only successful patches. If any arm has zero acceptances, its cost per acceptance is undefined. Unavailable usage is missing, not free. If an unknown billed component can change the primary cost decision and cannot be bounded, that decision remains unresolved.

## 4. Precision and multiplicity

Before scoring, use calibration to describe within-task variation and between-task heterogeneity. Four calibration task clusters are insufficient for a precise intraclass-correlation estimate, so evaluate a broad grid of plausible heterogeneity, paired system outcomes, deadline rates and correlated cost distributions. Include perfect/near-perfect task agreement and near-boundary acceptance rates. Do not import the reviewer's rough 25–30 point detectability estimate as a result.

The default sample is fifteen tasks with two core repetitions, prioritizing task diversity. The proposed method is paired task-cluster resampling (20,000 bootstrap draws with a frozen analysis seed), recomputing acceptance differences and cost-per-acceptance ratios in each draw. This is a candidate method that requires independent simulation/coverage review; registration currently records it as unvalidated.

For affirmative primary claims, propose four simultaneous one-sided bounds: lower Δ and upper R for each of the two supervisor systems. A Bonferroni allocation of α=0.05 across four bounds gives **98.75% one-sided bounds**. A system qualifies only if its lower Δ bound is at least −0.10 and upper R bound is at most 0.50. This controls the planned multiplicity conservatively only if the individual interval procedure has its claimed coverage.

A small or degenerate bootstrap distribution is not a precision certificate. Zero-acceptance resamples make cost bounds unbounded; boundary/constant outcomes, too few informative clusters or failed coverage validation prevent a confirmatory conclusion. Show descriptive paired results and clearly label uncertainty limitations instead of reporting an artificially tight interval.

Freeze the simulation scenarios, method, seed, coverage acceptance criteria and power report before scored dispatch. Target at least 80% simulated probability of recognizing a useful alternative (Δ=0, R=0.40) across the registered plausible scenarios, while checking family-wise false-positive behavior at the margins. If fifteen tasks cannot meet the precision target, either amend the sample **before scoring**, or explicitly register this study as feasibility-only. Expanding after a favorable intermediate comparison is not permitted by this design.

This draft defaults `confirmatory_claims_enabled` to false until that review succeeds. “Feasibility-only” still has explicit business targets, but its data cannot be presented as proof of the ten-point margin.

## 5. Primary price convention

Before scoring, freeze source URL, retrieval date, currency, per-million input/output prices, exact model and output/reasoning mapping. Prices remain identical for all runs regardless of collection date. Availability and rate-card completion are launch prerequisites.

For each model component m:

`C_reference_m = inclusive_input_m / 1e6 × list_input_price_m + billable_output_m / 1e6 × list_output_price_m`.

Sum worker/supervisor/planning components and paid retries once. Cached input is already inside inclusive input. Reasoning tokens already included in output are not added again. The **primary reference assumes no cache discounts**, so cache-read/write rate assumptions are outside this defined price model. Unmappable output billing semantics still create uncertainty and cannot be waved away.

This convention makes the counterfactual explicit for Codex. It does not estimate a subscription invoice, prove API portability, or predict quality/runtime on another provider. Report observed invoices, cache-aware estimates, subscription/access allocation and hosting/labor as separately labelled scenarios. The hypothesis's “half the cost” refers only to this frozen reference model cost; adoption economics must also inspect measured review effort and the user's real access arrangement.

## 6. Three-run Gemma portfolio

Collect Gemma repetitions 1 and 2 as core trials and a third independent candidate solely for the portfolio. This costs fifteen additional generations under the fifteen-task design. Under the superseded ten-task/three-repeat design no extra generation would have been needed, but all three runs would still incur economic cost.

For each task:

1. Freeze candidate ordering before dispatch.
2. Evaluate the trusted public predicate on all three frozen returns. Returns after the deadline or without a candidate artifact are ineligible.
3. Select the first public-passing candidate by that order; if none passes, return no candidate.
4. Commit the selection manifest before sealed outcomes or review scores are released to the selector or comparative analyst.
5. Grade only the selected artifact for the portfolio's operational success. A hidden failure of that candidate stays a portfolio failure even if a later candidate would pass secretly.

Charge all three generations and public selection checks to this fixed-batch policy. Report sequential aggregate runtime (up to 3T plus selection), rather than a fictitious parallel minimum. Machine-check compute and reviewer time are separate from reference inference cost. No additional review is counted when the same selected artifact's already-blinded review is reused, but count exactly one such review in the portfolio's per-delivery burden. A third-candidate selection receives the same review as any other eligible patch.

This yields **one portfolio observation per task**, not three and not three overlapping portfolios. Compare against the two-trial mean of each supervised system by task; the opportunity/deadline difference is explicit. Reused Gemma trials remain correlated evidence. Portfolio costs are alternatives, not additions to the physical study bill: count each executed call once in study totals.

The post-hoc oracle “at least one of three sealed passes” is a separately labelled upper bound. It cannot establish what a user could select from public feedback.

## 7. Time and review burden

Report subject dispatch-to-return time and verification/review latency separately. Primary delivery is **a submission by T that later passes verification**, not a claim the external review also finished by T.

Show the empirical cumulative fraction of all registered trials delivering an accepted submission by time t≤T. Early failures remain nondeliveries; treating their short runtimes as independent right-censoring would reward failure. A secondary capped-delivery-time summary assigns accepted runs their return time and nondeliveries T. Label this as a decision metric, not actual compute consumption. Report actual elapsed consumption for every endpoint separately.

Blinded review captures active minutes, verdict, requested changes, critical defects and adjudication for every machine-eligible patch. Report both reviewer measurements, reviewer-adjusted summaries, per-task distributions and paired subsets. Keep queue time and baseline familiarization separate. Include time spent on subsequently rejected candidates in total human minutes per accepted result. Mechanical operator effort and patch-review effort are distinct; neither is inferred from token counts or handoffs.

## 8. Staged continuation and reporting

Calibration is unscored. Scored stage one contains five preselected tasks and 55 generated runs. The checkpoint sees only feasibility/capture/evaluator information with model rankings masked; its criteria are in the protocol. Stage two contains the remaining ten preselected contracts and 110 runs. There is no effect-based interim stopping or task replacement.

If later task authors see stage-one outcomes, or contracts must change, register a separate cohort and show its results separately. If stopping at stage one, report a five-task feasibility cohort and no supported primary hypothesis. Maintain task qualification and construction logs so selective inclusion can be audited.

Report primary targets, estimates, bounds, readiness safeguards and missingness first. Then show secondary direct systems, whole supervisor systems, the public-selected Gemma portfolio, observed/subscription pricing and review burden. Describe residual harness, task-author and single-repository limitations. All AI and human roles remain visible.
