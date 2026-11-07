# Estimation and reporting methods

[registration.json](registration.json), sections `hypotheses`, `sample`, `analysis_plan`, `stopping_rule` and `pricing_rule`, holds all settings. This cohort estimates feasibility and tradeoffs. It does not establish noninferiority, test a joint economic claim or support a purchasing recommendation. The sample is too small for the proposed narrow-margin claim under plausible task heterogeneity; no numerical task requirement or power guarantee is inferred from the review's rough calculation.

## Focal estimates

For each task and system, average fresh trial acceptance indicators, then average tasks equally. Estimate the focal completion difference from paired task means. Report all secondary contrasts in their registered order without replacing the focal comparison with whichever looks best. Business targets are descriptive replication screens, not hypothesis-test thresholds.

For each arm, cost per accepted implementation equals total registered standardized model cost across all its attempts divided by core machine acceptances. Failures, deadline runs and paid retries remain in the numerator. Report the focal ratio and its denominators. Zero acceptances yield undefined cost per acceptance; unknown billable usage leaves economics unresolved unless decision-relevant bounds exist. Core acceptance is the frozen independent machine result. Human merge verdicts belong to the optional extension and do not gate the core denominator.

Report per-task paired outcomes and raw accepted counts beside aggregates. The task is the uncertainty cluster; repeated trials are not independent tasks. Use the registered paired task-cluster bootstrap draws, seed and descriptive interval level for differences, cost ratios and relevant time/effort contrasts. Resample complete task vectors, preserving every arm/trial and portfolio linkage. Independently review the analysis implementation and boundary handling before reporting.

Intervals are descriptive and unadjusted, with no familywise test or affirmative margin-crossing rule. Report the share of resamples with undefined/unbounded economic denominators; do not discard them. Constant/sparse task outcomes can yield misleadingly narrow bootstrap intervals: flag those intervals as uninformative, show the paired outcomes and seek larger independent replication. Do not label business targets established even if a small-sample interval happens to lie on one side.

## Missingness and deadline effects

A demonstrated delivery needs a timely final return and independent machine acceptance. Deadline, early incomplete, rejected, interrupted and unverified attempts remain distinct dispatched outcomes. Unrun schedule slots are missing. Show complete paired blocks plus conservative missing-outcome scenarios; do not manufacture failures or remove expensive attempts to improve a rate. Stage-specific reporting is required if collection ends early.

Report cutoff hits per arm in calibration and scoring, with numerators/denominators and descriptive uncertainty. Follow registration's imbalance flags before scoring. Plot the fraction of all dispatched trials yielding an accepted final submission by elapsed time. Early failures do not improve accepted-delivery speed and are not independently right-censored successes. The registered earlier-cutoff sensitivity uses frozen final-return timestamps only; it does not infer earlier working patches. Report actual consumed time and capped delivery time separately.

## Retry portfolio

Use the registered independent Gemma candidates and frozen selection order. Choose the first timely candidate passing the trusted public predicate; commit selection before sealed outcomes or reviewer results are exposed to the selector. No public pass means no selected artifact. A selected artifact's hidden failure remains a portfolio failure even if another candidate secretly passes.

Charge every candidate and public selection check to the fixed-batch policy. The portfolio is one observation per task and has the registered larger sequential opportunity. Reused core trials are correlated evidence. Count physical generations and human reviews once in study totals; per-policy attribution may reuse their cost explicitly. The oracle “any sealed candidate passes” is a labeled upper-bound diagnostic only.

## Prices and human effort

Freeze dated exact-model rate cards and verified billable token mappings. Standardized cost uses inclusive input and billed output once at registered uncached rates; cache and reasoning subsets must not be added twice. Reconcile OpenCode, LiteLLM and OpenRouter as views of the same calls. Inconsistent GLM reasoning/completion fields discovered during readiness require qualification, not an assumed subset relationship. Provider invoices and cache-write uncertainty are separate analyses.

Measure mechanical operator activity in core runs. If activated, the optional human-review extension separately measures active blinded review through verdict, including reviewed-but-rejected patches. Queue time, baseline familiarization, preparation and inference/runtime are separate. Show reviewer IDs/effects and blinding breaches. Report review minutes per eligible patch and total human minutes per accepted result, with undefined denominators explicit. Without the extension, review effort and merge readiness are not measured; missing review staffing does not block the core study or imply zero review cost. Labor/hosting monetization is an explicit scenario and must avoid charging the same time twice.

## Decision language

Present machine completion, defects and timeout effects first, then cost/time/effort estimates with uncertainty. Point estimates meeting business targets identify a candidate for larger task-diverse replication. Missed targets, provider drift or incomplete evidence remain informative feasibility outcomes. Neither favorable point estimates nor descriptive bounds establish the target margin. All AI, human, harness/provider and single-application limitations are disclosed.
