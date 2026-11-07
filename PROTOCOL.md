# Study 2 protocol — revision 4

**Draft for registration. No application or study runs have been produced under this protocol.** Revision 2 incorporates external design feedback. The [one-page overview](README.md) gives the decision question; [ANALYSIS_PLAN.md](ANALYSIS_PLAN.md) defines thresholds and analysis. The user chose a new small application with a real UI, API and local test database.

## 1. Hypothesis and decision

We expect that a strong supervisor may raise Gemma's verified delivery rate while retaining a useful model-cost advantage. The previous pilot provides no confirmation of that expectation.

The two primary comparisons are **Terra supervising Gemma versus Terra alone** and **GLM supervising Gemma versus Terra alone**. For either supervised system, the proposed target is a completion-rate difference of at least −10 percentage points and a standardized model-cost-per-acceptance ratio of at most 0.50. These are proposed business margins, requiring explicit registration before data collection.

A candidate meeting both targets only in its point estimates is promising, not established. Conservative joint uncertainty bounds, a viable absolute delivery rate and satisfactory independent review are needed to recommend a follow-up deployment validation. The analysis plan defines supported, contradicted and inconclusive outcomes. The broader set of pairwise comparisons is secondary.

Completion is a gate. Partial-work scores explain failures; they cannot turn an incomplete patch into accepted delivery. The prior study had written requirements, but executable verification, post-hoc grading, scope, infrastructure and missing human-effort measurement all limited interpretation. Scope was a possible contributor, not a proven sole cause.

## 2. Application and independent construction

Use a small work-item tracker, provisionally `Workboard Lab`: TypeScript, a React UI, real HTTP API, local SQLite persistence, users/workspaces, session authentication and basic CRUD. Freeze exact framework versions, baseline commit, lockfile, runtime image and fixtures before scored collection. Hosted services and production deployment are outside this fixture.

The [application and documentation plan](APPLICATION_AND_DOCS_PLAN.md) proposes Next.js/React, Better Auth, better-sqlite3, Vitest and Playwright, with registry-verified candidate pins in [docs/corpus-plan.json](docs/corpus-plan.json). Candidate availability is not runtime qualification. Eligible builders validate the stack and freeze the actual lockfile/image; documentation setup follows those versions and records any release-family coverage gaps. That plan also defines the seven session-role adapters and concrete corpus acceptance evidence.

Separate the subject application from a restricted control environment containing sealed tests, reference solutions, raw logs and the evaluator. Subjects receive only the task's baseline, contract, public checks and permitted documentation. Containers or equivalent identities/mounts enforce separation; worktrees alone are insufficient. Each task/run starts from the same baseline with isolated writable dependencies, caches, ports and database.

### Construction provenance and family exclusion

Human builders are preferred. If construction uses models, appoint models outside **all three subject families**: Gemma/Google's Gemma family, GLM/Z.ai's GLM family, and Terra/OpenAI's GPT family. Broader uncertain family membership is resolved before appointment. Record exact model IDs, families, providers and human contributions for the baseline, each reference patch, alternate implementation and every test/check artifact.

Subject models and their families may execute the calibration tasks as subjects; those outputs remain calibration evidence and are excluded from reference solutions and acceptance authoring. The current coordinator's protocol writing is disclosed separately from fixture construction. An independent reviewer who did not author an artifact qualifies it. This exclusion reduces one bias; it does not prove independence of training data or architecture.

Builders and reviewers remain unassigned in registration. The study waits for eligible construction/review capacity rather than quietly using a subject model to fill those roles.

### Database boundary

The proposed workload needs initialization and task-related changes in disposable local test databases. Before execution, register explicit permission for those isolated databases; the original Minutes restriction on non-Beads database mutation is not silently carried over or lifted for other databases. This draft executes no migrations. Production databases and credentials remain inaccessible.

## 3. Task contracts and public versus sealed checks

Freeze fifteen independent task contracts and a seeded task order before scored dispatch. Each task is one coherent behavior, with explicit examples, boundaries, non-goals, ownership and compatibility rules. Tasks never inherit another run's implementation.

Candidate task categories include validation, archive/restore, stable pagination, transactional import, export fidelity, ownership, dependent UI state, rejected-save recovery, calendar dates and version conflicts. Fifteen tasks must be distinct problems rather than cosmetic parameter changes to manufacture extra task clusters. Final contracts, category balance and difficulty strata remain unresolved until independent construction.

**Public material:** all requirements, baseline regressions, build/typecheck/lint commands and representative task examples. Public tests are intentionally incomplete examples of the disclosed contract, not an exhaustive copy of the final evaluator.

**Sealed material:** independently authored inputs, boundary combinations, persistence/ownership checks and integration scenarios derived from those same requirements. Subjects see neither sealed test code nor its feedback during a primary run. After all primary collection, report public-check pass and sealed acceptance separately. A solution that only matches visible examples can pass publicly and fail final acceptance.

Every sealed assertion maps to a requirement the subject received. Hidden requirements, exact internal helper names and gold-patch-specific structures are excluded. UI contracts specify accessible roles, names and labels. Playwright checks use `getByRole`, `getByLabel` or an equivalent semantic locator, with any exception justified before registration. Accessible naming is a stated product requirement, not a secret selector assumption.

Use [TASK_TEMPLATE.md](TASK_TEMPLATE.md) for the mapping, provenance and qualification record.

## 4. Qualification before a task is scored

Each task needs:

1. A clean baseline whose regressions pass and whose task acceptance fails for the intended reason.
2. A complete reference patch passing every applicable gate.
3. A materially different valid implementation of the acceptance-sensitive path, independently reviewed, demonstrating that checks accept implementation freedom. A second complete application is unnecessary.
4. Negative controls proving each critical requirement can reject a plausible incomplete/wrong patch: for example UI-only persistence, missing validation or wrong-owner access.
5. Baseline/reference replays in three freshly initialized environments with expected outcomes. These are three clean instances of the frozen environment, not three platforms.
6. Independent contract/evaluator review with actual author/reviewer identities, family provenance, timestamps and signoff.

Qualification can proceed in stages: four calibration tasks first, then five scored tasks, then ten more. All fifteen scored contracts, task order and difficulty strata are frozen before stage one. The remaining ten's implementation/check authors stay blind to stage-one model identities, rankings, patches and failure patterns. If that separation cannot be maintained, qualify all fifteen before scoring or treat later tasks as a separately registered cohort.

This staging reduces upfront qualification work without letting favorable outcomes choose later tasks. Expected reviewer effort and build effort are recorded as study setup overhead.

## 5. Acceptance and review

The external evaluator applies each frozen endpoint patch to a clean baseline and runs trusted checks outside the subject's writable environment. Its scripts, public-check copy and dependencies cannot be replaced by a subject's test edits.

A patch is machine-eligible only when all applicable behavioral, UI/API/database, authentication/ownership, regression, build, typecheck, lint, scope and integrity checks pass. Subjects may add tests, but those additions supplement the trusted suite. Legitimate changes to baseline expectations are specified and checked in the contract.

Machine-eligible patches receive blinded review. Final acceptance also requires resolution of critical defects found under the frozen review rules. A missing check or unresolved critical review is unverified; a reproduced defect is rejected. Minor style preferences affect review outcomes, not the functional acceptance rule.

If the evaluator is defective after registration, preserve original results and suspend the affected task across every configuration. Correct the evaluator under a new hash and apply it consistently to all affected frozen endpoints. Report original and corrected analyses separately. Required contract changes create a new cohort rather than rewriting what a subject was asked to do.

## 6. Models and five core systems

| Model | Exact requested ID | Route |
|---|---|---|
| Gemma 4 | `google/gemma-4-31b-it` | OpenCode → LiteLLM → OpenRouter |
| GLM | `z-ai/glm-5.3-flash` | OpenCode → LiteLLM → OpenRouter |
| Terra | `gpt-6.1-terra` | Codex, high reasoning |

Verify live availability, resolved revisions, provider routing and settings before registration. Existing OpenCode selectors to reverify are `litellm-gemma-experiment/gemma-implementation` and `litellm-glm-experiment/glm-planning`. Historical CoreWeave/Relace routes are not proof of current availability. Disable unregistered fallbacks/delegation and preserve any unavoidable provider/revision variability in the manifest.

The core systems are Gemma alone, GLM alone, Terra alone, Terra supervising Gemma and GLM supervising Gemma. Each receives the same task contract and performs its own planning. There are no cross-imported model plans in this core design. A fixed checklist and append-only ledger replace required Beads decomposition, consistently across systems.

The supervisor can select work, inspect quality, interpret public diagnostics and request repairs. Gemma performs all application/test edits. Both supervisors use the same deterministic Gemma broker, with separate sessions and usage. A supervisor cannot supply a complete replacement implementation. Terra alone is one complete Codex agent, not an agent plus a second operator.

**Harness interpretation:** The proposed core still places Terra in Codex. “Terra supervisor versus GLM supervisor” therefore means **Codex/Terra/Gemma versus OpenCode/GLM/Gemma**, not an isolated supervisor-model effect. A separate [Terra/OpenRouter readiness check](readiness/terra-openrouter-20261107.md) now establishes basic OpenCode transport/tool capability. Adopting that common harness requires an explicit registration revision and full common-harness qualification.

## 7. Controlled conditions

Freeze baseline/task hashes, role prompts, relevant skills, version-local documentation, explicit checking protocol, allowed tools, sandbox permissions, host resources, context/output settings, sampling, compaction and retry policy. Use equivalent shell/read/search/edit/test capabilities and remove unrelated MCP/global skills. Keep supported-setting differences visible rather than pretending all harnesses are identical.

Configure and qualify the available relevant MCP servers under [MCP_SETUP.md](MCP_SETUP.md). The common bundle includes a required documentation capability, starting with the installed Context MCP (`@neuledge/context`, currently `library-docs`) and exact-version docs selected from the new application's lockfile. Evaluate the available local-docs, Serena, GitNexus and Lightpanda servers for relevant coverage, isolation and harness parity; record inclusion/exclusion before calibration. Every direct agent, supervisor and worker receives the same approved corpus and capabilities. Freeze versions, tool schemas, role permissions, source/index hashes, network policy and timeout/retry behavior. Global catalogs and prior-project indexes are not the study configuration. MCP and corpus qualification hashes are launch dependencies; installation alone does not satisfy them.

Install dependencies before timing. Execute sequentially with fresh sessions, task-only Git history, independent writable state and logged access. Keep credentials in the controller/broker, restrict network to required inference/transport, and isolate private evaluations and other runs. Record provider cache counters; fresh local caches do not guarantee a cold remote cache.

The neutral controller dispatches only the frozen schedule and FAQ, captures events and performs logged mechanical recovery. Product coaching, patch edits and adaptive task decomposition belong to the registered agents, not the operator. Material missing product answers trigger task-validity review across systems.

## 8. Calibration and precision

Use four disposable task contracts covering at least two categories and a range of independently assessed difficulty. Run five systems twice per task: **40 unscored runs**. Begin with one repetition on two tasks (10 runs) to test plumbing; those are included in the 40, not added to it.

Calibration itself has a **120-minute workflow deadline**. Validate native usage semantics, transport retries, supervision, independent acceptance, negative controls and human-review timing. The construction team receives only authorized aggregate difficulty/variance diagnostics; subject code is not reused in fixture artifacts.

Estimate within-task repeat variability and between-task heterogeneity. Four clusters give a rough diagnostic, not a reliable population variance estimate. Simulate plausible heterogeneity grids as well as the calibration estimate before choosing a confirmatory precision claim. Inspect floor/ceiling signals: if Terra always passes and Gemma always fails, or every system always passes/fails, investigate difficulty and gate validity. Use broad task categories and independent difficulty strata, not tasks selected to make a particular workflow win. Any calibration redesign is logged before scored contracts are frozen.

The default allocation is **15 tasks × 2 repetitions** for the core. Calibration may justify a different pre-scoring registration, but it does not automatically change the design after seeing scored outcomes. Neither “25–30 points is detectable” nor “a 10-point margin is established” is assumed; both depend on clustering and outcomes. The precision simulation and independent analysis-method review are launch artifacts.

## 9. Finite, uniform stopping rule

Revision 2 replaces the unlimited runtime proposal with a generous wall-clock deadline; dollar/token budgets remain uncapped.

For scored runs, propose:

`T_minutes = min(120, max(30, ceil(5 × median accepted-calibration subject minutes)))`

Freeze one numeric T for all five systems before scoring. Compute the median from verified accepted calibration returns, pooling systems/tasks under the registered allocation; record the eligible rows. At least one verified accepted return is needed from two systems and three calibration tasks. If this is unavailable, calibration has not qualified the design. Its observed imbalance and truncation are reported; the 30–120 minute bounds prevent pathological medians.

The clock runs from dispatch to the complete agent's or supervisor's final return. Tool waits, inference waits, worker handoffs and retries use the same clock; it never resets for a child worker. Setup is outside the clock. Independent evaluation/review latency is separate from the subject deadline and separately reported.

At T the controller terminates the workflow, freezes its state and labels it **not delivered by deadline**. A later audit may find working code, but it cannot turn a missing timely final delivery into primary success. A final return before T is delivered only if independent acceptance subsequently passes. Early incomplete returns also count as not delivered, not as fast accepted work.

Actual API exhaustion or an account-level outage stops dispatch for the whole collection, not only the currently expensive arm. Preserve active attempts and incomplete blocks, restore the environment before any registered continuation, and report operational interruptions separately. Account credits are not the experimental stopping threshold. Account readiness is checked before each block without logging credential values or imposing a spending cap.

User stop, safety/protocol violation and concrete unrecoverable infrastructure failure remain endpoints. The analysis plan handles missingness and incomplete blocks; they cannot silently yield a favorable noninferiority conclusion.

## 10. Sample, retry control and staged collection

Core: 15 tasks × 5 systems × 2 repetitions = **150 runs**. Add a third Gemma-alone run per task for **15 extra runs**. Total scored generation is **165**. The first two Gemma runs are the core observations; the third is reserved for the retry portfolio. One additional run is not independent evidence for another core arm.

The public-check-selected Gemma portfolio generates three independent candidates. It chooses the earliest candidate in preregistered order passing the entire trusted public-check predicate, then submits that selected artifact to sealed acceptance. Selection never sees hidden acceptance, reviewer grades or another model's judgment. If none passes publicly, the portfolio fails. Account for all three generations and public selection checks, even if candidate one would have sufficed. This is a fixed-batch control, not a claim about early-stopping retries.

Each constituent run has deadline T, so the sequential portfolio can consume up to **3T plus selection time**. It is a secondary practical retry policy with a larger aggregate opportunity, not a time-matched primary arm. Report an oracle “any sealed pass among three” only as a diagnostic upper bound, not as a deployable selector. [ANALYSIS_PLAN.md](ANALYSIS_PLAN.md) defines denominators and reuse.

Freeze seeded task order and position-balanced configuration order before dispatch. Execute complete task/repetition blocks sequentially; schedule the third Gemma run under its recorded independent slot. At the five-task checkpoint, **55 scored generation runs** have been collected; the remaining ten account for **110**. This is one third of the scored task set, not half.

Continue only on a blinded feasibility review: correct model/baseline resolution for every run, all endpoint snapshots/statuses captured, no unresolved evaluator/integrity defect, native usage captured for at least 95% of completed calls with every missing call listed, complete required review timing, and capacity to qualify remaining tasks under the pre-frozen contracts. Any unresolved criterion means pause and document a protocol/environment version boundary. Relative model performance is excluded from the checkpoint. If the study ends at five tasks, report a feasibility cohort; no primary hypothesis is declared supported.

## 11. Human review as an outcome

Operational human effort remains separately timed; it may be small by design. The main human-effort comparison is **blinded patch review**.

Two independent human reviewers assess every machine-eligible patch with the same task contract, baseline access and machine evidence. Hide model, harness, price, runtime and session identity. Randomize and balance assignments; record reviewer effects and possible recognition of repeated tasks or stylistic clues. Model panels may assist only in a separately declared analysis, not silently replace these reviewers.

Each reviewer times active inspection/reproduction through a verdict: “merge,” “changes requested,” or “cannot assess,” with reasons and confidence. Queue/waiting and one-time baseline familiarization are recorded separately. Reviewer edits are outside this measurement. A reproduced critical defect enters the acceptance adjudication; a stylistic preference does not override a passing functional gate.

Include review minutes for patches that pass machine checks but are rejected at review. Report minutes per reviewed patch and total operational-plus-review minutes per finally accepted result. Also report paired review comparisons on tasks accepted by both systems, with reviewer IDs and selection effects visible. This measures assessment burden, not the unknown time to implement requested repairs.

Reviewer identity, independence, timers and the critical-defect/merge rubric must be frozen before scoring. Missing review data cannot be treated as zero or justify a claim about total human cost.

## 12. Measurement and pricing

Record UTC/monotonic dispatch, first/last events, process exit, deadline status, evaluator/review intervals, role/session IDs, prompt/model/config hashes, all source patches, checks, native usage and provider cross-checks. Distinguish input, cached input, reasoning/output subsets and cache writes without double counting. Validate incremental/cumulative counters on calibration; retain paid failures/retries and unavailable fields explicitly.

Keep supervisor, worker, coordination, fixture construction, calibration, grading and publication usage separate. Record public check/repair cycles, supervisor requests, worker handoffs and human interventions as different measures. Plans are internal to each workflow and included in delivery usage.

**Primary economic rule:** freeze a dated list-price input/output rate card for each exact model and compute uncached API-equivalent cost on inclusive input and billed output once. This deliberately standardizes away cache discounts and subscriptions; it is a counterfactual model-usage comparison, not a Codex or OpenRouter invoice. Output definitions and reasoning inclusion follow the frozen native/provider mappings. Unmapped billable usage makes the economic comparison unresolved.

Observed API invoices, known-cache repricing, hosting, subscription allocation and labor dollars are secondary scenarios. Preserve cache-write uncertainty. Human minutes and runtime are reported in their own units; monetization uses explicit assumptions and avoids double counting. Setup/review overhead appears both separately and in optional fully attributed economics.

## 13. Reporting, corrections and future work

Report all scheduled/dispatched attempts, endpoint statuses, accepted counts, deadlines and missing data. Rank decision evidence by completion first; distinguish point targets from uncertainty-qualified conclusions. Present a plain-language answer to each primary hypothesis, plus secondary retry/harness comparisons and per-task evidence. Broad weighted scores remain optional preference tools, not completion substitutes.

A first final return is frozen before grading. Any later acceptance-guided repair is a new registered extension with uniform feedback and its own time/usage; sealed-test feedback makes those tests no longer held out. Fixture changes, provider/model drift and hardware changes are versioned rather than pooled silently.

Potential later treatments include GLM supervising Terra, reciprocal reviewer roles, Beads, alternate MCP bundles, self-hosted serving and another repository. The qualified common MCP bundle is now part of the proposed core setup; comparing bundles would be a separate treatment. Published plan/economic scenarios do not constitute those experiments.

The immediate milestone is appointing eligible fixture builders, qualifying calibration and validating the measurement/deadline method. Publication does not start collection or select a winner.

## References

- [SWE-bench evaluation guide](https://www.swebench.com/SWE-bench/guides/evaluation/): clean containerized patch evaluation informs the reproducible evaluator design.
- [OpenAI: Separating signal from noise in coding evaluations](https://openai.com/index/separating-signal-from-noise-coding-evaluations/): ambiguity, restrictive tests and weak coverage motivate task/evaluator qualification.
- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents): distinguishes tasks/trials, agent outcomes and different repeated-trial success measures. Our public-only selector is an operational policy, unlike an oracle pass-at-k score.
- [NIST: Comparing Instruments](https://www.nist.gov/publications/comparing-instruments): distinguishes difference and equivalence comparisons for binary/continuous outcomes. It does not provide a power guarantee for this task-clustered design.
