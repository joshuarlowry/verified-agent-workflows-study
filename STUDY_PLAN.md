# Study execution plan

Determine whether supervision makes Gemma a practical alternative to Terra doing the work itself. Execute the design in [registration.json](registration.json); that file remains authoritative for models, routes, settings, counts, deadlines and analysis. This plan orders the work and identifies the evidence required to advance. See [live collection status](setup/RUN_STATUS.md) for actual dispatches and endpoints; this document describes the execution sequence.

## Question and decision

The focal comparison is **Terra supervising Gemma versus Terra alone**. The working expectation is that supervision improves delivery while preserving enough of Gemma's cost advantage. The registered business screen is a completion rate within 10 percentage points of Terra at at most half its standardized model cost per accepted implementation.

This cohort estimates feasibility and tradeoffs. Meeting those point targets justifies larger, task-diverse replication; it does not establish noninferiority or justify purchasing. Zero acceptances make cost per acceptance undefined. Missing billable usage can leave the economic conclusion unresolved. Completion is a hard gate; cheap early failures are not fast delivery.

The secondary comparisons cover GLM supervision, GLM alone, Gemma alone, and a public-selected three-candidate Gemma portfolio. Keep these secondary even if their results look more favorable.

## Fixed study systems

| Workflow | Complete implementation agent | Supervisor | Application and test editor |
|---|---|---|---|
| Gemma alone | Gemma | — | Gemma |
| GLM alone | GLM | — | GLM |
| Terra alone | Terra | — | Terra |
| Terra supervising Gemma | — | Terra | Gemma |
| GLM supervising Gemma | — | GLM | Gemma |

All roles use the common OpenCode → LiteLLM → OpenRouter path. Exact requested/resolved IDs, ZDR provider pins, precision, reasoning settings and fallback restrictions come from registration and the frozen launch manifest. Only Gemma 4, GLM and Terra are launched. Context documentation is the only MCP treatment; every role also receives the same read-only documentation files.

The work is performed against **Workboard Lab**, the planned application baseline ([clean reconstruction status](fixtures/README.md)), with a Vite/React UI, Hono API, Better Auth sessions and a disposable local SQLite database. Each task is an independent increment on that same baseline. No task inherits another implementation or a builder's conversation.

## Starting position

Current gates and evidence live in `application_preparation`, `harness_decision`, `documentation_corpus`, `launch_blockers` and `clean_restart` in [registration.json](registration.json). [Preparation status](setup/README.md) links the recorded construction/review evidence; [run status](setup/RUN_STATUS.md) reports current job transitions in Eastern time. Preparation test totals are not study results. No pre-reset fixture/broker/evaluator signoff is eligible for this cohort.

## Responsibilities

- **Coordinator:** maintain registration, deterministic controller, isolation, capture, scheduling, evidence and reporting. During scored runs, give only the frozen prompt/FAQ and logged mechanical recovery. Do not choose tasks or repair a standalone agent's work after its return.
- **Fixture builders and reviewers:** appoint only the three authorized models in separate recorded sessions. Another model reviews each substantive baseline, reference, alternate, evaluator, contract, FAQ, prompt and corpus artifact. Record author/reviewer identities, routes, sessions and hashes. Do not allow self-approval.
- **Standalone agent:** owns planning, implementation, tests, self-review and its final return.
- **Supervisor:** owns task direction, backlog and review; Gemma makes all application/test edits. Record every handoff, intervention, revision and response, with supervisor and worker usage separate.
- **External evaluator:** runs trusted checks outside subject access against the frozen endpoint. It provides no sealed diagnostic feedback during a primary attempt.

This is AI managed under human direction. Subject models help build and cross-review their own benchmark. Fresh sessions reduce conversation carryover but do not establish independent-family authorship. The coordinator's protocol/harness work retains its own attribution. Human patch review is an optional later extension, not a core gate or an implicit zero-cost activity.

## Phase 0 — Clean restart after the streaming defect

The clean-cohort policy and ID live in registration. All uncertified pre-fix model-authored source, tests, contracts/FAQ approval, prompts, corpus qualification and reviews are excluded. Original attempts remain in audit history and historical preparation overhead. No calibration or scored attempt existed to rerun.

First finalize/cross-review the source-guarded transport repair and mandatory verified gateway launcher. Freeze their hashes and prove actual native tool/file fidelity, raw capture and accounting for Gemma, GLM and Terra sequentially. Missing startup proof or incomplete streams block dispatch. Use fresh sessions, workspaces, writable dependencies/caches and controller logs.

Next revalidate public requested-scope text, rebuild baseline/tests and model-authored harness/corpus/prompt/evaluator artifacts without old solution, test, conversation or review access. Public scope is provisional until freshly reviewed; trusted upstream package/document bytes are reusable only with exact provenance and fresh qualification. Regeneration is not permission to change the five treatments or select favorable tasks.

This transport-only gate authorizes clean construction, not calibration. Phases 1 and 2 can exchange freshly reviewed baseline/docs inputs as required; both must fully qualify before Phase 3.

## Phase 1 — Finish the common harness

Use generic/disposable probes rather than scored tasks while repairing infrastructure. Keep raw logs private and publish sanitized manifests and evidence.

1. **Verify the frozen source.** Check the registered historical baseline commit/source prefix and application tree ID, current `fixtures/baseline` export, lockfile, image and browser/native-module dependencies. Ensure fresh exports contain only approved source and public inputs. Do not copy this repository's history, reference patches, prior runs or controller logs into subjects.
2. **Finish real worker launch.** Implement the registered Gemma adapter behind one immutable broker interface shared by both supervisors. Qualify fresh sessions, supported continuation, request identity, public handoff extraction, errors and explicit retries. Stream raw logs outside subject access; the prototype's aggregate output cap must not become an unregistered early-stop condition.
3. **Complete accounting.** Preserve raw provider and native events, call/session/parent IDs, attempts, timestamps and missingness. Resolve normalizer U4/U5 and all-model mappings. Test paid failures, duplicate/conflicting events, cache subsets and supervisor/worker attribution. For GLM, use verified provider completion tokens for billing; do not add reasoning or reconstruct billing from the native split.
4. **Connect all stop paths.** Test native parent final return, worker handoff, deadline, user stop, API exhaustion, outages and logging/storage failure. Include budget errors carried inside successful HTTP streams. Account exhaustion stops new dispatch globally. Quiesce the entire workflow, including detached writers, before recording an immutable endpoint. Failed freeze is an integrity failure, not a successful snapshot.
5. **Qualify actual Context access and role permissions.** Exercise the registered corpus through direct Gemma, direct GLM, direct Terra, both supervisors and each broker-launched worker role. Verify exact library allowlists, source/file parity, attribution, invalid-library rejection, timeouts and crash behavior. Check effective tools and global skill access; the existing failed browser-skill invocation alone does not establish denial. Mount the frozen Context module at the path required by the corpus launch command.
6. **Qualify one workflow.** Use the registered primary single lane and verify aggregate resources, isolated dependencies/caches/databases and actual provider behavior. Concurrent-lane work is deferred; any later concurrency extension requires an explicit amendment and qualification before dispatch.
7. **Cross-review and freeze.** Review substantive adapter/controller changes with another authorized model. Freeze prompt/FAQ/handoff bundles, provider settings, tools, permissions, image/lockfile/corpus, commands and usage semantics. Retain secrets only outside published manifests.

**Exit:** real role and handoff probes pass; raw usage reconciles within declared limits; late writes and hidden/sibling access are rejected; actual cutoff/final snapshots work; resource scheduling qualifies. Resolve the applicable canonical launch blockers with evidence, not descriptions of intended behavior.

## Phase 2 — Qualify the task bank

Start by freshly reviewing baseline/task/FAQ scope, then constructing and cross-reviewing the baseline and public regression suite from that scope. Do not inherit the retired implementation/tests. Next construct the four calibration contracts. Then qualify the first five scored tasks before committing to the remaining construction workload. All fifteen scored contracts and the stage allocation must be frozen before scored collection. Later reference/check builders must remain blind to earlier comparative outcomes.

Use [TASK_TEMPLATE.md](TASK_TEMPLATE.md) for every task:

1. Review the disclosed outcome, boundaries, FAQ, permissions, persistence and compatibility requirements. Map every public and sealed assertion to a public requirement. Sealed checks introduce new cases, not secret requirements or a reference solution's markup.
2. Construct the evaluator from the contract and baseline in a separate session without reference-solution access. Keep checks outside subject read/write access. Use role/label UI locators, real HTTP/authentication flows and disposable database evidence where applicable.
3. Build a complete reference and a materially different valid implementation in separate sessions. Their purpose is to establish solvability and reject implementation-specific oracles; they are not scored attempts or subject context.
4. Prove baseline regressions pass and requested behavior fails for the intended reason. Prove the reference and alternate pass applicable acceptance gates. Prove negative controls reject critical omissions, including relevant ownership, persistence and UI/API inconsistencies.
5. Replay baseline/reference qualification in three clean environments. Check the alternate against the relevant full acceptance gates. Review contract/check consistency and all substantive artifacts with a different authorized model; retain exact hashes, commands, exits and failures.
6. Freeze the trusted public selection predicate separately from sealed results. Preserve all legitimate baseline expectation migrations enumerated by the contract.

The first scored block should cover distinct categories rather than five similar UI edits. **Proposed qualification slate:** S01 validation, S03 pagination, S06 permissions, S07 failure recovery and S15 keyboard/focus. This is a planning proposal, not a registered allocation: confirm solvability, coverage and difficulty, then record final IDs/strata before scoring. Do not replace tasks because of which model wins.

**Initial exit:** qualify C1 and the common actual model/corpus/capture/endpoint path, then collect the already registered ten-workflow C1 calibration block. Qualify C2–C4 before their slots and the first five scored packets before scoring. All scored contracts remain frozen before scoring; later builders remain blind to comparative outcomes. A broken task is repaired and requalified before dispatch, never silently scored as agent failure.

## Phase 3 — Calibrate the whole workflow

Run the registered **40 calibration workflows**: four tasks × five systems × two fresh trials. Start with qualified C1 across all five systems twice: ten sequential workflows included in those forty. Its order is frozen in `calibration_initial_block` in registration; its admission and exact frozen evidence are recorded in `calibration_initial_block` and the linked admission receipt. Qualify remaining calibration packets before their slots. Use one primary lane and a fresh baseline for every attempt. Concurrent collection is deferred unless explicitly amended and qualified.

Measure route resolution, endpoint capture, public/sealed acceptance, usage, handoffs, mechanical operator activity, deadline hits and infrastructure interruptions. Preserve early returns and failures. No operator continuation prompts or unregistered rescue.

Review:

- Whether tasks expose meaningful variation rather than uniform floors/ceilings.
- Whether repetition or task differences dominate variability, as descriptive evidence for future study design.
- Deadline hits by arm, including the registered 25% absolute and supervised-minus-reference review flags. A flag pauses scoring for scope/cutoff review; any redesign is registered and recalibrated uniformly.
- Complete capture, evaluator consistency, tool/corpus parity and resource/rate effects.

Reforecast duration from measured calibration. Any revised task, prompt, deadline, route or harness needs a documented freeze/requalification boundary. Preserve original calibration results. This cohort stays feasibility/estimation; calibration does not promote it to confirmatory status.

**Exit:** a recorded calibration decision, reviewed artifacts and no unresolved launch/integrity defect. Populate applicable registration hashes, seeds, actual task IDs and freeze fields. Do not invent signoff timestamps or mark null fields complete without evidence.

## Phase 4 — Freeze and collect scored attempts

Freeze the task-balanced, seeded schedule and portfolio selection order before the first scored dispatch. Use the same baseline and public task inputs for each arm, with no planning-stage solutions imported between systems.

| Block | Physical workflow attempts | Continuation condition |
|---|---:|---|
| First five scored tasks | 55 | Complete capture and valid evaluators; outcome-blinded integrity review |
| Remaining ten tasks | 110 | Remaining tasks qualified without earlier outcome exposure |
| Total scored | 165 | Includes one extra Gemma generation per task |

Each core system gets two fresh trials per task. Gemma gets a third candidate for the portfolio. Select the first timely candidate passing the frozen trusted public checks in the preregistered order **before** revealing sealed outcomes to the selector. Charge all three candidates and selection checks; this policy has three times the sequential opportunity, not the direct arm's single-run deadline. Count physical calls once in study totals.

For every attempt:

1. Preinstall independent dependencies, initialize only its disposable database, prestart approved services, verify model/provider/settings and mount/tool manifests, and record setup separately.
2. Dispatch one frozen role/task prompt. Record UTC and monotonic start, first event, sessions and hashes. The uniform 120-minute deadline covers the complete workflow, tools, waits, retries and all handoffs.
3. Capture passively. A complete agent/supervisor final return is the primary endpoint; a worker return is a handoff. Operator actions are mechanical and logged. No hidden acceptance feedback reaches the subject.
4. Quiesce and freeze source, execution backlog if used, logs and status before grading. Run the trusted public predicate and sealed evaluator in separate clean environments with reliable exit codes. Preserve the original endpoint even if incomplete.
5. Record timely accepted, rejected, early incomplete, deadline, interrupted and unverified outcomes distinctly. Unrun slots remain missing. Provider drift stops new dispatch and creates a separately registered boundary; account exhaustion stops admission globally.

The stage-one continuation review uses the registration's integrity/capture criteria, including native usage on at least 95% of completed calls with every missing call listed. Relative performance must not determine continuation. Do not pool repaired endpoints into primary results.

## Phase 5 — Analyse and publish

Publish completion and defects before economics. Use equal task weighting and the paired task-cluster analysis in [ANALYSIS_PLAN.md](ANALYSIS_PLAN.md), including descriptive intervals, sparse/undefined bootstrap draws and incomplete-block sensitivity.

Report for every workflow:

- Acceptance counts/rates, task-level outcomes, failure categories and known defects.
- All-attempt standardized model cost divided by accepted implementations, with failures/retries included; provider invoices and cache/hosting scenarios separately.
- Accepted-submission curves, actual consumed wall time and capped delivery time. Early incomplete returns cannot win on delivery speed.
- Supervisor interventions/handoffs and worker usage separately; measured mechanical operator effort; human merge-review effort as **not measured** unless the optional extension runs.
- Preparation, calibration, scoring, evaluation and reporting overhead separately; physical study totals without double-counting reused portfolio candidates.

Release one current report with sortable outcome tables, completion/time/cost comparisons, exact rate assumptions, manifests, sanitized logs and endpoint references. Keep raw credentials, sealed material during collection and upstream content without publication clearance private. Preserve audit versions in Git/private artifacts rather than placing competing plans in the current tree.

Disclose AI management, subject-family fixture authorship, shared training/priors, prompt provenance, model/provider precision and opacity, the single application, small task sample, serving drift, missing data and optional human-review limits. A public price calculator changes economic assumptions only; it does not simulate changed runtime or quality on other hardware/providers.

## Schedule and immediate next work

The registered forecast covers **205 workflows** including calibration. Read the current generated forecast in [README.md](README.md) and assumptions in registration. Revision12 selects sequential collection and prioritizes the first C1 ten-workflow block. Forecasts exclude construction, qualification and outages and must be replaced with measured calibration estimates. No aggregate dollar or token cap is imposed.

The first task milestone is **one qualified C1 packet plus the real common supervisor-worker path**, after the registered source, transport, runtime and documentation gates. Consult canonical evidence for completed gates rather than treating this phase ordering as a status ledger. Finish C1's reference/alternate/external-check/negative-control packet; finish real Gemma broker launch, all-model capture and cutoff/final freeze; cross-review both. Then expand qualification to the remaining calibration tasks and role matrix. Calibration follows the gates above, not the existence of a runnable prototype.
