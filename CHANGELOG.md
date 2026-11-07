# Protocol revision notes

## Revision 2 — response to design review

Status remains draft. These edits change the proposed experiment, not any observed results.

| Review concern | Change |
|---|---|
| No expected result or decision margin | Two primary supervision-versus-Terra hypotheses; proposed −10 percentage-point completion margin and ≤0.50 reference cost-per-acceptance ratio; point estimates, supported bounds and inconclusive outcomes distinguished |
| Too many comparisons | Only two primary comparisons; other contrasts are explicitly secondary |
| Thin precision | Default 15 tasks × 2 core trials; four-task calibration variance diagnostics; pre-scoring simulation/coverage review; confirmation disabled until precision qualifies |
| Unlimited runs | Calibration cap 120 minutes; one scored cap based on 5× accepted calibration median, bounded 30–120 minutes; no dollar/token cap; global stop for account exhaustion |
| Supervisor/harness confound | Terra stays in Codex; supervisor contrast explicitly names whole systems; shared-harness Terra is an unverified future treatment |
| Cheap retry control | Public-selected Gemma three-run portfolio with deterministic selection; 15 additional runs under the two-trial design; all three costs and up to 3T sequential opportunity disclosed |
| Subscription versus API prices | Primary frozen uncached API-equivalent rate card; actual bills, cache-aware pricing and subscriptions remain scenarios |
| Human effort near zero by construction | Timed blinded “would I merge this?” review of every machine-eligible patch, including patches rejected during review |
| Visible versus hidden checks | Representative public examples versus sealed new cases of disclosed requirements; separate public-pass and final-acceptance reporting |
| UI selectors overfit markup | Public accessibility contracts and semantic role/label locators with preregistered exceptions |
| Fixture author bias | Exact artifact authorship recorded; all three subject families excluded from application/reference/check construction; current coordinator eligible for protocol writing only |
| Qualification burden | Qualify four calibration tasks, then five scored tasks, then ten; freeze all scored contracts/order upfront and keep later builders blind to stage-one outcomes |
| Staged run feasibility | Initial 10 calibration runs included within 40; scored stages 55 + 110 = 165; blinded continuation criteria, no effect-based optional stopping |
| Readability and registration | README is the short overview; formulas and inference move to ANALYSIS_PLAN.md; schema v2 adds hypotheses, pricing, review, provenance, stopping and stage controls |

The review's approximate detectable-effect size is not adopted as a power result. Calibration must inform simulations, and a small task set may remain insufficient for the proposed ten-point decision margin. Primary price standardization is deliberately uncached; its economics are a reference convention, not actual Codex cost.

## Revision 1

Initial draft: ten tasks, three repetitions, five configurations; unlimited runtime; no numerical business margins. Preserved in Git history at `bd35bc1`.
