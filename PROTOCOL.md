# Study 2 proposal: verified delivery of small software changes

**Status: draft for review, not a registered or started experiment.** Prepared November 7, 2026 UTC. The user selected a new small application with a real UI, API and local test database. This document proposes the experiment; it does not create the application, run subjects, change spending limits or alter the first study's results.

## Decision to answer

Which practical agent system most reliably delivers an accepted software change, and what model cost, elapsed time and human effort does that delivery require?

Completion is an eligibility gate. A cheap, fast, incomplete return cannot win by offsetting failure with a weighted score. Partial work remains useful diagnostic evidence, but is not accepted delivery.

The previous study had written behavioral requirements. The identified weaknesses include incomplete executable verification, acceptance-binding gaps, post-hoc grading, broad feature scope, infrastructure interruptions and unmeasured human effort. Scope may have contributed; the pilot does not establish it as the sole cause.

## Recommended design at a glance

| Decision | Proposal |
|---|---|
| Application | New, small work-item tracker, provisionally `Workboard Lab` |
| Stack | TypeScript, React UI, real HTTP API and local SQLite persistence; exact framework and versions frozen during fixture preparation |
| Core configurations | Gemma alone; GLM alone; Terra alone; Terra supervising Gemma; GLM supervising Gemma |
| Workload | 10 independent task contracts, each a complete, narrow change |
| Repetitions | 3 fresh sessions per task/configuration: 150 scored runs |
| Calibration | 2 separate disposable tasks × 5 configurations: 10 unscored runs |
| Main outcome | Verified completion at the first agent/supervisor final return |
| Cost outcome | Total arm expenditure, including unsuccessful attempts, per accepted implementation |
| Other outcomes | Acceptance latency, time to endpoint, active human minutes, repair/check cycles and supervisor interventions |
| Run order | Sequential execution; randomized, position-balanced configuration order within task/repetition blocks |
| Spending | No imposed dollar or token budget; actual API exhaustion remains an endpoint |
| Interpretation | Practical model-plus-harness systems, not isolated model capability |

150 is the proposed sample size, not a spending cap or a power calculation. Thirty runs per configuration are three repeats on ten tasks, not thirty independent task types. If the study ends early, report the achieved sample and every unrun slot.

## 1. Build and qualify the fixture before selecting winners

Create two separate repositories or access domains:

- **Application repository:** minimal product baseline, subject-visible documentation and existing regression tests. Every scored workspace starts at the same immutable commit.
- **Study control repository:** registration, scheduler, evaluator, reference solutions, hidden test implementations, logs and results. Subjects cannot access this repository, earlier runs or sibling workspaces. Publish sanitized materials after collection; keep credentials and unreleased acceptance code private.

The application should support users, workspaces and work items through real browser/API/database flows. Include session authentication, ownership boundaries, basic CRUD and a small existing regression suite. Avoid hosted authentication, cloud databases, paid APIs, email delivery and unrelated infrastructure. Production deployment is outside scope.

Baseline construction must finish before scored tasks. All baseline regressions, type checks and lint must pass from a clean checkout. Build the baseline once; do not let each subject scaffold its own application. Pin the Git commit, dependency lockfile, runtime/container image, database schema, fixtures and local documentation.

Each task branches independently from this baseline. Task 2 never inherits Task 1's implementation. Task-specific fixtures may vary, but the frozen fixture pack is identical across configurations for the same task.

**Database authorization boundary:** the proposed study needs execution against disposable local test databases, including initialization and task-required schema changes. The original Minutes experiment prohibited non-Beads database mutation. Registration must explicitly authorize only these isolated test databases before execution. This plan does not execute any database changes or authorize access to production data.

A small purpose-built repository limits representativeness and may favor its author's conventions. Record who authored it, use independent fixture review, and describe conclusions as applying to this workload. A later replication on an existing repository is a separate study.

## 2. Task portfolio: ten narrow, independently accepted changes

The following are candidate task shapes, not the final frozen contracts. Validate their feasibility in the completed baseline before registration. Do not choose or replace tasks based on which tested model wins.

| Candidate | One requested outcome | Illustrative acceptance boundary |
|---|---|---|
| Paired numeric bounds | Create, edit and clear optional estimates consistently | Zero/unset distinguished; stored-plus-patch validation; UI/API/storage agree |
| Archive and restore | Archive one work-item entity without losing history | Default list excludes archived items; restore preserves identity and notes; ownership preserved |
| Stable pagination | Page a filtered work-item list without duplicates or omissions | Stable tie handling; filter and sort preserved; explicit empty/last-page behavior |
| Transactional import | Import a bounded CSV format atomically | Invalid row rejects the batch with no partial writes; valid data persists; ownership assigned correctly |
| Round-trip export | Export a documented set of fields accurately | Escaping, empty values and identifiers follow the published contract; reload/round-trip verified |
| Ownership boundary | Close one explicitly identified cross-user access gap | Authenticated owner succeeds; other owner and unauthenticated requests are rejected through real HTTP paths |
| Dependent form fields | Keep a dependent selection valid after its parent changes | Invalid selection clears; unrelated edits do not clear valid state; saved value matches the visible choice |
| Failed-save recovery | Recover correctly from a rejected optimistic UI edit | UI rolls back or clearly retains unsaved state according to contract; retry succeeds; no duplicate write |
| Calendar-date boundary | Apply one date-only availability rule | Valid calendar dates, inclusive boundary and timezone-independent behavior; no hierarchy or holiday subsystem |
| Version conflict | Reject a stale update without overwriting newer work | Two sessions produce a reproducible conflict; latest stored value survives; UI provides the specified recovery |

Aim for one coherent behavior per task, usually a few acceptance criteria, even when it crosses UI/API/storage layers. Exclude broad redesigns, multi-feature epics, unspecified policy decisions and tasks whose completion depends on external services. Do not use file count or self-authored test count as a quality target.

Balance the final portfolio across validation, persistence, authorization, UI state and compatibility. Record task selection and difficulty estimates before subject runs. Calibration tasks must not be reused as scored tasks.

## 3. Prove that the acceptance gate works

Every task receives a signed-off contract using [TASK_TEMPLATE.md](TASK_TEMPLATE.md). Its pack contains the request, exact observable behavior, non-goals, examples, compatibility rules, permitted changes, public checks and a requirement-to-test map. All requirements are visible to subjects. Hidden checks may vary data and exercise boundaries; they cannot introduce secret requirements or mandate unrequested internal names/designs.

Before registration, for **each** task:

1. Run the evaluator on the unchanged baseline. Existing regressions must pass; at least one task-specific acceptance check must fail for the expected reason.
2. Run a complete reference solution. Every applicable gate must pass in a fresh environment.
3. Demonstrate implementation freedom with an independently reviewed alternative valid solution or a materially different implementation of the acceptance-sensitive path. Tests should depend on public behavior, not a gold patch's helper names.
4. Test deliberately incomplete or defective variants: bypassed validation, wrong-owner access, UI-only state without persistence, omitted boundary behavior, or another task-relevant defect. Each critical requirement needs a documented negative control that its check catches.
5. Run the baseline/reference validation on three clean environments. Investigate inconsistent outcomes; do not register known flaky tasks.
6. Have a reviewer who did not author the task/checks review the contract, mappings, reference behavior and negative controls. Record the reviewer and actual review. AI assistance alone must not be advertised as independent human verification.

These are launch requirements, not optional post-study analysis. Unqualified tasks are revised or removed **before** registration, with reasons.

### Acceptance rule

An endpoint is **accepted** only when all applicable gates pass on its frozen source snapshot:

- Every declared behavioral requirement, including boundary/error cases.
- Real UI → HTTP API → test database behavior for relevant tasks, including reload/persistence.
- Authentication/ownership checks and preserved baseline regressions.
- Frozen build, typecheck and lint commands with reliable exit codes.
- Test and evaluator integrity, scope compliance, and absence of unresolved critical defects under the predeclared review rules.

A skipped test, failed adapter, inaccessible database or unresolved critical check is **unverified**, never a pass. A known failure is **rejected**. Passing tests supports acceptance against the declared contract, not universal defect freedom.

Run the independent evaluator outside the subject's writable environment. Apply the endpoint application patch to a clean baseline, use trusted checks rather than subject-edited scripts, and prevent access to evaluator source, secrets and artifacts. Subject-written tests are retained as evidence but cannot replace trusted tests. Legitimate baseline expectation changes must be anticipated in the task pack and verified by trusted updated checks; agents cannot remove regression guarantees to pass.

If an oracle defect is found after registration, freeze the affected task's interpretation for **all** configurations. Record the defect, retain original results, version the corrected evaluator and rerun all affected frozen endpoints where valid. Label corrected analysis separately. Do not repair one model's evaluator adapter and quietly compare it with others' earlier results.

## 4. Models, routes and configurations

Reuse the exact requested models:

| Model | Requested ID | Harness and route |
|---|---|---|
| Gemma 4 | `google/gemma-4-31b-it` | OpenCode → LiteLLM → OpenRouter |
| GLM | `z-ai/glm-5.3-flash` | OpenCode → LiteLLM → OpenRouter |
| Terra | `gpt-6.1-terra` | Codex, high reasoning; never through OpenRouter |

Previous selectors were `litellm-gemma-experiment/gemma-implementation` and `litellm-glm-experiment/glm-planning`. Reverify both for the roles used. Previously observed provider routes were CoreWeave for Gemma and Relace for GLM; those are historical observations, not a claim of current availability.

Before registration, verify live availability and resolve immutable model revisions where supported. Freeze provider routing, disable fallbacks and uncontrolled delegation, and record actual response IDs. If a revision/provider cannot be pinned, disclose that residual variable. If routing or model revision changes during collection, stop new dispatches, retain affected attempts and register a separate environment stratum; do not silently substitute.

### Core comparison

| Reader-facing configuration | Who plans/reviews? | Who edits application code and tests? |
|---|---|---|
| Gemma alone | Gemma | Gemma |
| GLM alone | GLM | GLM |
| Terra alone | Terra in Codex | Terra in Codex |
| Terra supervising Gemma | Terra in Codex | Pinned Gemma worker only |
| GLM supervising Gemma | GLM in OpenCode | Pinned Gemma worker only |

All receive the same task contract. Each configuration owns its planning and self-review. There are **no cross-imported model plans** in the core experiment. Record planning time and usage, but do not multiply the design into a planning-source experiment.

The neutral controller selects only the preregistered task/run order. It cannot choose implementation subtasks, interpret failures into suggestions, improve plans or edit subject code. Product questions receive the same frozen FAQ. A material unanswered question triggers task-validity review across all configurations, not a bespoke answer for one agent.

Supervisors may select work, inspect diffs, interpret diagnostics and request repairs. They may not edit application/test code or supply a complete replacement implementation. Use the same deterministic worker broker, checked before both supervisor treatments. Record every handoff and separate supervisor/worker usage. Terra alone has one complete Codex agent, not an additional Terra operator.

For this small-task study, replace required Beads decomposition with a simple, common task checklist and append-only event ledger. This is a proposed change from Study 1, held constant across core arms. Beads/Dolt setup and plan-import fidelity are not research variables here; reintroducing them would be a separate workflow treatment.

## 5. Freeze the variables that can be controlled

| Variable | Required control |
|---|---|
| Application and task | Same baseline and same task-pack hash for matched runs |
| Instructions | One common behavior/checking protocol; only explicit role-specific differences |
| Skills/docs | Same relevant, version-local content; no unrelated global skills or optional MCP services |
| Agent tools | Equivalent shell, read/search/edit, test and documentation capabilities; no extra models |
| Feedback | Same explicit checking protocol; disable harness-only helpful hooks if no equivalent exists |
| Dependencies | Install before timing from the same lockfile; isolated writable dependencies and caches |
| Machine resources | Same host/resource allocation, sequential runs, independent ports and databases |
| Isolation | Separate containers/identities/mounts, task-only source/history, logged network/file access; worktrees alone are insufficient |
| Credentials/network | Credentials stay in the controller/broker; no production access; only required inference/transport endpoints allowed |
| Session memory | Fresh session and workspace per repetition; no previous plans, attempts or feedback |
| Sampling/context | Freeze supported settings, compaction, output/context limits and retry behavior; record unsupported differences |
| Cache | Fresh local agent/build caches; record provider input/cache buckets and request timestamps; do not claim remote cache state is controllable |
| Evaluation | Frozen evaluator image, acceptance suite, seeds, fixtures and trusted commands |
| Human input | Mechanical operations only during scored runs; all active attention and actions logged |

The Codex/OpenCode distinction remains. No claim of a pure model comparison is justified. Hardware changes, self-hosted serving and different tool stacks belong in separate replications; price overrides alone do not test those systems.

## 6. Run lifecycle and endpoints

1. Prepare the isolated checkout, dependencies and test database before starting the task clock. Confirm the expected baseline state.
2. Dispatch the frozen role prompt and task pack; record UTC and monotonic timestamps, prompt hashes and session IDs.
3. Agent or supervisor works autonomously, uses public feedback and performs its own repairs. Public task checks and existing regressions are available equally to all arms. The sealed evaluator remains outside subject access.
4. At the first agent/supervisor final return, freeze source, patch, transcript, task state and usage **before** independent grading. Worker returns inside a supervised run are handoffs, not workflow endpoints.
5. Run the frozen acceptance gate, classify the endpoint and record verification latency separately from subject elapsed time.
6. Publish the endpoint and defects honestly, including a candid but incomplete return. Never turn a quick failure into a speed win.

Other endpoints remain actual API-budget exhaustion, explicit user stop, concrete unrecoverable infrastructure block, or a recorded safety/protocol violation. There is no imposed dollar/token budget and no automatic wall-time cutoff. Passive 30-minute/hourly observations may record liveness without prompting progress. A running but repetitive agent is not silently declared complete or restarted.

### Repair policy

The primary experiment measures first-return delivery, including all agent/supervisor repair work **before** that return. Public failed-check cycles, supervisor repair requests and actual human interventions are separate counters.

Do not resume a failed endpoint just because another arm succeeded. If externally guided repair is studied, register it as a secondary extension for **every eligible failed endpoint**, with an identical machine-generated acceptance receipt and explicit continuation/stopping rules. Freeze the primary outcome first, include all extension expense and measure whether acceptance is reached. Any disclosed sealed-test feedback ends its status as a held-out test; use that description honestly. The repair extension is not automatically authorized or mixed into core results by this proposal.

### Infrastructure failures

Classify outages and model failures from predefined evidence rules. Preserve dispatches, paid failures, retries, partial patches and first endpoints. Use only frozen, identical transport retries that cannot duplicate successful work. Failed requests with no subject response may be retried mechanically; ambiguous delivered requests must be reconciled before replay. A resumed/replaced interrupted run gets an explicit attempt identity and linkage, never an overwritten record.

## 7. Calibration, registration and collection

**Preparation:** build fixture and task packs; implement capture/evaluation; appoint reviewers. No scored work begins here.

**Calibration:** run two disposable tasks through all five configurations once (10 runs). Exercise UI/API/database checks, native usage accounting, provider cross-checks, supervisor handoffs and endpoint capture. Include known-bad and valid evaluator fixtures. Do not reuse calibration task solutions as subject examples.

**Registration gate:** freeze 10 qualified scored tasks, all manifests/prompts, model routes, scoring rules, trial count, randomized order/seed and analysis plan. Every required field in [registration.json](registration.json) must be resolved; it currently contains explicit nulls. Record task/reviewer approvals and the explicit disposable-database permission. Calibration failures may change the draft, with a changelog; scored outcomes may not retroactively change it.

**Collection:** 10 tasks × 3 repetitions × 5 configurations = 150 primary runs. Use complete task/repetition blocks, one configuration at a time. Randomize task block order; construct a seeded schedule that balances each configuration's early/late positions. Commit the generated schedule before dispatch. Repetitions share task difficulty and must be analyzed as clustered observations.

**Checkpoint:** after the first complete scored block, audit only transport, capture and evaluator integrity. Do not select winners, remove difficult tasks, tune prompts or change task scope. A substantive harness fix creates a version boundary; preserve earlier results and register how comparability is handled.

**Reporting:** independently verify endpoints, finish blind review/adjudication, then unblind and compare. No purchasing recommendation based solely on partial quality scores or mean time to an incomplete return.

## 8. Measurements and analysis

For every run capture:

- Model/provider resolution, exact settings, prompt/config hashes and role/session IDs.
- Dispatch, first event, last event, process exit, evaluator start/end, and observable setup/outage/wait intervals.
- Native input, output, cached-input, reasoning and cache-write counters, including their provenance and known subset relationships. Validate incremental/cumulative semantics in smoke tests; deduplicate event IDs.
- Provider-reported costs where available; native usage reconciliation as cross-checks, never additive double counting. Keep Codex access/subscription allocation distinct from hypothetical token pricing.
- Source/evaluator hashes, exit codes, individual gate results, endpoint category and any unresolved check.
- Public check cycles, failed checks followed by repair, supervisor requests/handoffs, and manual feedback events. Do not equate a tool call, model turn, supervisor handoff and human intervention.
- Active human attention using explicit start/stop activity records and reason codes (setup, mechanical repair, product clarification, review, adjudication). Idle waiting is not active labor. Missing timing remains unknown; the study must not fabricate zero.

Keep fixture construction, acceptance authoring, calibration, coordination, grading and publication overhead separate from subject work. Show both incremental operational cost and fully attributed study expenditure. Planning is part of each task's delivery cost, not a shared plan cost in this design.

### Primary and secondary outcomes

| Outcome | Definition and restriction |
|---|---|
| Operational completion rate | Accepted original endpoints / all dispatched original runs; interrupted/unverified attempts do not count as accepted |
| Evaluable acceptance rate | Accepted / (accepted + rejected), reported separately with all exclusions and counts; never hide operational failures in this denominator |
| Cost per accepted implementation | Total measured cost of all dispatched attempts in that arm, including failures/retries, divided by accepted count; zero accepted means undefined |
| Time to accepted delivery | Dispatch through frozen endpoint plus verification/required critical-review latency for accepted attempts; subject, machine-evaluation and human-review intervals also shown separately |
| Time to endpoint | Report for every run, labelled by outcome; fast failed returns are not successful delivery times |
| Human effort | Active minutes and intervention events per attempted and per accepted task; unknowns remain unknown |
| Repair burden | Check/repair cycles and supervisor interventions before the primary endpoint; any post-return extension separately labelled |
| Accepted-code quality | Predefined maintainability/clarity/test-adequacy review among accepted results; never substitutes for acceptance |

Do not add tokens, dollars, minutes and human effort into one quantity. Monetized compute/access/labor needs explicit units and assumptions; avoid charging the same labor twice. If costs are incomplete, label the cost-per-acceptance value a known-cost subtotal per accepted result, not a complete invoice.

Report per-task paired outcomes, task-category results, repetition variability and raw counts. Use task-clustered uncertainty estimates for aggregate differences; ten task clusters offer limited precision. Conditional speed/quality comparisons among accepted runs can select different task sets, so also report paired comparisons on tasks accepted by both configurations and identify the subset. Register comparisons before collection:

- Each direct model against the other direct models.
- Terra supervising Gemma versus Gemma alone and Terra alone.
- GLM supervising Gemma versus Gemma alone and GLM alone.
- Terra versus GLM as Gemma supervisor.

Present completion first, then cost/time/effort tradeoffs. A weighted calculator may explore preferences among eligible outcomes, with incomplete data still unresolved; it must not rank failed attempts as successful alternatives.

## 9. Independent evaluation and quality review

The deterministic gate is the primary acceptance authority. Task/check authors and subject implementers do not certify their own work alone.

A separate reviewer audits the task contracts before registration. After collection, two reviewers assess anonymized patches for maintainability, clarity and test adequacy using a frozen, evidence-linked rubric. Hide configuration/session/cost information and randomize review order; acknowledge that coding style can still reveal identity. Record disagreements and adjudication.

A model panel can assist with finding defects, but correlated judgments by the same subject models are not independent proof. Critical alleged defects require a reproducible case and consistent adjudication across affected results. A reviewer vote cannot waive a failed functional gate. Until required critical review is resolved, the endpoint remains unverified.

Reviewer availability is an explicit launch dependency. If only AI review is available, revise and disclose that limitation before registration; do not claim an independent human study after the fact. Study management, task authorship, implementation, evaluation assistance and report authorship must each disclose AI involvement.

## 10. Optional follow-up treatments

Keep these out of the five-configuration core so their effects can be identified:

- GLM supervising Terra, and Terra supervising GLM, as a reciprocal stronger-model pair.
- Gemma reviewing Terra's implementation, paired with Terra reviewing Gemma, if role-swapping itself is the question. Standardize review authority; code-review-only and active task supervision are distinct workflows.
- An acceptance-guided repair extension with a uniform feedback policy.
- Self-hosted inference or different hardware/quantization/serving parameters.
- Beads, additional MCP tools or a different agent harness.
- Replication on an existing repository and fresh task portfolio.

Register each chosen extension with its own hypotheses, task set, settings and allocation before running it. Never treat repriced old tokens as an observed hardware or orchestration result.

## 11. Deliverables and launch checklist

Deliverables before scored dispatch:

- Frozen application baseline and reproducible build/test image.
- Ten task contracts, requirement mappings, reference/alternative validation and negative controls; two separate calibration tasks.
- An executable acceptance runner that emits accepted/rejected/unverified plus criterion evidence, with real database/browser verification where relevant.
- Frozen five-configuration manifest, prompt templates, worker broker and verified capture semantics.
- Signed reviewer/task qualifications, disposable-database permission, randomized schedule and completed registration.
- Private raw artifact archive with a sanitized public export procedure.

Deliverables after collection:

- Every endpoint, accepted or not; execution/source/evaluator hashes and exact check results.
- Completion rates and denominator accounting; accepted-delivery costs/time/effort; partial-work diagnostics kept separate.
- All interventions, outages, plan/check cycles, costs and unavailable measurements.
- Human/AI review provenance, review/adjudication timestamps, disagreements, limitations and any corrected analyses.
- A readable report that starts with verified completion and clearly separates observations from pricing scenarios.

The immediate next milestone is **qualifying the new fixture and two calibration tasks**, not launching 150 runs. A registered experiment starts only after the acceptance gate and capture system are demonstrated to work.

## Methodological references

The proposed protections are informed by primary-source evaluation guidance, not an endorsement of copying a public benchmark wholesale:

- [SWE-bench evaluation guide](https://www.swebench.com/SWE-bench/guides/evaluation/): describes applying candidate patches and running evaluation in containerized environments. We adopt clean, reproducible execution, while using our own newly qualified tasks.
- [OpenAI: Separating signal from noise in coding evaluations](https://openai.com/index/separating-signal-from-noise-coding-evaluations/): identifies underspecified requests, overly restrictive tests, weak coverage and contradictory requirements as sources of invalid coding evaluation. This motivates contract review, behavioral tests and positive/negative controls here.
- [Study 1 protocol](https://github.com/joshuarlowry/minutes-agent-workflow-study/blob/main/public/data/protocol.md) and [published disclosure](https://github.com/joshuarlowry/minutes-agent-workflow-study#ai-management-and-study-gaps): local evidence for the differences this proposal makes explicit.
