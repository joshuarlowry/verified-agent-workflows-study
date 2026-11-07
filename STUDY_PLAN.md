# Study execution plan

Determine whether supervision makes Gemma a practical alternative to Terra doing the work itself. Execute the design in [registration.json](registration.json); that file remains authoritative for models, routes, settings, counts, deadlines and analysis. This plan orders the work and identifies the evidence required to advance. No calibration or scored run has started.

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

The work is performed against **Workboard Lab**, the current [application baseline](fixtures/baseline), with a Vite/React UI, Hono API, Better Auth sessions and a disposable local SQLite database. Each task is an independent increment on that same baseline. No task inherits another implementation or a builder's conversation.

## Starting position

| Component | Evidence available | Work remaining |
|---|---|---|
| Application | Different-model source review and three clean full-check container replays | Final launch export/image/lockfile verification |
| Contracts | Four calibration and fifteen scored candidates under [fixtures/contracts](fixtures/contracts) | Per-task references, alternative paths, external checks, negative controls and qualification |
| Documentation | Source/extraction cross-review of rebuilt corpus | Actual role integration, tool/file parity, containment and publication attribution |
| Isolation | Physical resource, mount, loopback and group-freeze probes | Real controller endpoint races, failure handling and full role boundaries |
| Agent transport | Synthetic native OpenCode and generic Context retrieval | Actual provider/corpus/broker sessions and complete usage reconciliation |
| Worker broker | Cross-reviewed synthetic candidate | Registered worker adapter, reliable handoffs and real stop/snapshot integration |

See [current preparation status](setup/README.md) and [machine-readable evidence](setup/status.json). Existing check totals are preparation evidence, not study results. The broker candidate explicitly refuses registered dispatch; filling hashes alone does not make it usable.

## Responsibilities

- **Coordinator:** maintain registration, deterministic controller, isolation, capture, scheduling, evidence and reporting. During scored runs, give only the frozen prompt/FAQ and logged mechanical recovery. Do not choose tasks or repair a standalone agent's work after its return.
- **Fixture builders and reviewers:** appoint only the three authorized models in separate recorded sessions. Another model reviews each substantive baseline, reference, alternate, evaluator, contract, FAQ, prompt and corpus artifact. Record author/reviewer identities, routes, sessions and hashes. Do not allow self-approval.
- **Standalone agent:** owns planning, implementation, tests, self-review and its final return.
- **Supervisor:** owns task direction, backlog and review; Gemma makes all application/test edits. Record every handoff, intervention, revision and response, with supervisor and worker usage separate.
- **External evaluator:** runs trusted checks outside subject access against the frozen endpoint. It provides no sealed diagnostic feedback during a primary attempt.

This is AI managed under human direction. Subject models help build and cross-review their own benchmark. Fresh sessions reduce conversation carryover but do not establish independent-family authorship. The coordinator's protocol/harness work retains its own attribution. Human patch review is an optional later extension, not a core gate or an implicit zero-cost activity.

## Phase 1 — Finish the common harness

Use generic/disposable probes rather than scored tasks while repairing infrastructure. Keep raw logs private and publish sanitized manifests and evidence.

1. **Verify the frozen source.** Check the registered historical baseline commit/source prefix and application tree ID, current `fixtures/baseline` export, lockfile, image and browser/native-module dependencies. Ensure fresh exports contain only approved source and public inputs. Do not copy this repository's history, reference patches, prior runs or controller logs into subjects.
2. **Finish real worker launch.** Implement the registered Gemma adapter behind one immutable broker interface shared by both supervisors. Qualify fresh sessions, supported continuation, request identity, public handoff extraction, errors and explicit retries. Stream raw logs outside subject access; the prototype's aggregate output cap must not become an unregistered early-stop condition.
3. **Complete accounting.** Preserve raw provider and native events, call/session/parent IDs, attempts, timestamps and missingness. Resolve normalizer U4/U5 and all-model mappings. Test paid failures, duplicate/conflicting events, cache subsets and supervisor/worker attribution. For GLM, use verified provider completion tokens for billing; do not add reasoning or reconstruct billing from the native split.
4. **Connect all stop paths.** Test native parent final return, worker handoff, deadline, user stop, API exhaustion, outages and logging/storage failure. Include budget errors carried inside successful HTTP streams. Account exhaustion stops new dispatch globally. Quiesce the entire workflow, including detached writers, before recording an immutable endpoint. Failed freeze is an integrity failure, not a successful snapshot.
5. **Qualify actual Context access and role permissions.** Exercise the registered corpus through direct Gemma, direct GLM, direct Terra, both supervisors and each broker-launched worker role. Verify exact library allowlists, source/file parity, attribution, invalid-library rejection, timeouts and crash behavior. Check effective tools and global skill access; the existing failed browser-skill invocation alone does not establish denial. Mount the frozen Context module at the path required by the corpus launch command.
6. **Qualify equal resources.** Start sequentially. Compare the same app/check workload alone and under both proposed lanes, with registered aggregate resources per workflow, isolated dependencies/caches/databases and measured provider-rate behavior. Apply the registered contention threshold. If it fails, amend to sequential collection before calibration; do not silently mix schedules.
7. **Cross-review and freeze.** Review substantive adapter/controller changes with another authorized model. Freeze prompt/FAQ/handoff bundles, provider settings, tools, permissions, image/lockfile/corpus, commands and usage semantics. Retain secrets only outside published manifests.

**Exit:** real role and handoff probes pass; raw usage reconciles within declared limits; late writes and hidden/sibling access are rejected; actual cutoff/final snapshots work; resource scheduling qualifies. Resolve the applicable canonical launch blockers with evidence, not descriptions of intended behavior.

## Phase 2 — Qualify the task bank

Start with the four calibration contracts. Then qualify the first five scored tasks before committing to the remaining construction workload. All fifteen scored contracts and the stage allocation must be frozen before scored collection. Later reference/check builders must remain blind to earlier comparative outcomes.

Use [TASK_TEMPLATE.md](TASK_TEMPLATE.md) for every task:

1. Review the disclosed outcome, boundaries, FAQ, permissions, persistence and compatibility requirements. Map every public and sealed assertion to a public requirement. Sealed checks introduce new cases, not secret requirements or a reference solution's markup.
2. Construct the evaluator from the contract and baseline in a separate session without reference-solution access. Keep checks outside subject read/write access. Use role/label UI locators, real HTTP/authentication flows and disposable database evidence where applicable.
3. Build a complete reference and a materially different valid implementation in separate sessions. Their purpose is to establish solvability and reject implementation-specific oracles; they are not scored attempts or subject context.
4. Prove baseline regressions pass and requested behavior fails for the intended reason. Prove the reference and alternate pass applicable acceptance gates. Prove negative controls reject critical omissions, including relevant ownership, persistence and UI/API inconsistencies.
5. Replay baseline/reference qualification in three clean environments. Check the alternate against the relevant full acceptance gates. Review contract/check consistency and all substantive artifacts with a different authorized model; retain exact hashes, commands, exits and failures.
6. Freeze the trusted public selection predicate separately from sealed results. Preserve all legitimate baseline expectation migrations enumerated by the contract.

The first scored block should cover distinct categories rather than five similar UI edits. **Proposed qualification slate:** S01 validation, S03 pagination, S06 permissions, S07 failure recovery and S15 keyboard/focus. This is a planning proposal, not a registered allocation: confirm solvability, coverage and difficulty, then record final IDs/strata before scoring. Do not replace tasks because of which model wins.

**Exit:** calibration tasks and first scored block have complete qualification packets; all scored contracts have reviewed scope; remaining construction has a credible outcome-blinded path. A broken task is repaired and requalified before dispatch, never silently scored as agent failure.

## Phase 3 — Calibrate the whole workflow

Run the registered **40 calibration workflows**: four tasks × five systems × two fresh trials. The initial ten-workflow smoke block is included in those forty, not additional scored evidence. Register the calibration order before dispatch; use the qualified lane policy and fresh baseline for every attempt.

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

The registered forecast covers **205 workflows** including calibration. Under its assumptions, qualified two-lane collection is about **4.47 days continuously or 13.40 eight-hour days**; the all-cutoff scenario is **12.01 or 36.04 days**. These are planning assumptions, exclude construction/qualification/outages and must be replaced by a calibration-based forecast. Do not assign a confident preparation completion date before the first task packet and real handoff qualify. There is no aggregate dollar or token cap.

The next milestone is deliberately small: **one qualified calibration task packet plus the real common supervisor-worker path**. Finish C1's reference/alternate/external-check/negative-control packet; finish real Gemma broker launch, all-model capture and cutoff/final freeze; cross-review both. Then expand qualification to the remaining calibration tasks and role matrix. Calibration follows the gates above, not the existence of a runnable prototype.
