# Study protocol

All current design choices, numbers, model/provider routes, versions and staffing gates live in [registration.json](registration.json). The [generated overview](README.md) presents them. This document defines execution rules; historical revisions do not override the registration. This cohort is explicitly for feasibility and estimation. A confirmatory study would require a new registration and broader independent tasks.

## Construct and qualify

Eligible builders outside the subject model families construct the small UI/API/database application, reference solutions, alternate valid paths and acceptance checks. Record human/model authorship, family, provider and artifact hashes. The coordinator's protocol and transport work does not qualify it for fixture authorship. An independent qualifier signs each artifact. See the registration's `construction_provenance` and `launch_blockers`.

Each task has one disclosed user outcome, explicit boundaries, permissions, compatibility behavior, non-goals, public examples and a frozen FAQ. Tasks are independent baseline patches. Freeze all scored contracts, task strata and schedule before the first scored stage. Later fixture authors remain blind to earlier results; otherwise qualify all tasks first or register a separate cohort.

A task qualifies when baseline regressions pass, the requested behavior fails for the intended reason, a complete reference passes, a materially different valid path passes, plausible critical omissions are rejected by negative controls, and clean-environment replays agree. Use [TASK_TEMPLATE.md](TASK_TEMPLATE.md). UI contracts require accessible roles/names/labels; tests use semantic locators and justify exceptions before dispatch. Sealed cases cover disclosed requirements using new inputs/combinations, without prescribing a reference implementation's markup or helpers.

The external evaluator applies each frozen endpoint patch to a clean baseline. Trusted checks are outside subject write access. Full acceptance requires every applicable behavior, UI/API/persistence, ownership, regression, build, typecheck, lint, scope, integrity and critical-review gate. Subject tests supplement trusted checks. Machine eligibility and final reviewed acceptance are separate outcomes.

## Harness, providers and tools

Use the single harness and approved MCP server specified by `harness_decision` and `mcp_setup`. Configure provider pins, no fallback, required retention policy and model-specific settings in the common gateway before qualification. Verify resolved revisions and catalog quantization, which are serving-system characteristics, not proof of identical weights. No unregistered delegation; supervised workflows use only their registered supervisor and pinned Gemma broker.

Qualify one OpenCode adapter, then verify role permissions and configuration inheritance on direct, supervisor and worker sessions. The supervisor may plan/select/review and own bookkeeping; Gemma performs application/test edits. The supervisor may request repairs but not supply a complete replacement implementation. The complete standalone agent owns its planning, verification and return. Context content review and setup follow [MCP_SETUP.md](MCP_SETUP.md).

The current direct provider probes establish limited ZDR/tool capability. Full streamed tool-result handling, native usage semantics, Context access and the broker must pass through the pinned OpenCode/LiteLLM path before calibration. Resolve unsupported tool selection and usage mappings explicitly; do not weaken privacy or silently switch providers/models. Record paid failures and every repair.

## Isolation and controller

Separate subjects from sealed tests, reference patches, controller logs, previous runs and sibling workspaces using containers or equivalent identities/mounts. Worktrees alone are insufficient. Each run gets the same task-only baseline/history and isolated writable dependencies, caches, browser profiles, ports and database. Install and prestart approved services before timing. Verify both process cwd and inherited PWD. Expose only approved source docs and the local app; restrict external networking to required inference transport.

Disposable local database initialization/mutation requires the registration's authorization gate. Production resources remain inaccessible. Author and execute fixture schema/reset operations only within the authorized local test environment. No production deployment, push or merge occurs from subject sessions.

The neutral controller dispatches the frozen schedule/FAQ, captures logs and performs logged mechanical recovery. It does not choose implementation tasks, inspect quality to steer, supply diagnostic hints, edit patches or repeatedly prompt an early-returned agent to continue. Product decisions beyond the frozen FAQ trigger task-validity review across arms. Supervisor interventions are part of the treatment and fully recorded.

## Calibration, deadlines and scheduling

Use the sample and fixed cutoff in registration. The cutoff is chosen before calibration and is not derived from accepted direct-agent runtimes. It includes model/tool waits, retries and worker handoffs without resetting; setup and later external review are separate. A complete-agent/supervisor final return freezes the endpoint even if early and incomplete. A worker return is a handoff. Deadline termination freezes the source and records non-delivery. No rescue of the primary endpoint.

Calibration reports completion, early return, cutoff hits and infrastructure interruptions per arm with counts/denominators. Apply the registered timeout-imbalance flags before scoring. A flag requires a documented scope/cutoff review and decision; any redesign needs a new frozen calibration version applied to all arms. Preserve original attempts. Report accepted-submission curves and the registered earlier-cutoff sensitivity, which classifies final endpoints without inspecting later patches. Do not imply that a patch existed earlier than its final return.

Calibration also checks difficulty/floor/ceiling patterns, within-task variation, provider usage, role handoffs, reviewer timing and isolation. Task difficulty revisions occur before scored contracts freeze and do not target a preferred model. There is no power/confirmatory promotion gate in this estimation cohort.

Freeze seeded, balanced sequential run order before dispatch. Include every scheduled/dispatched attempt. At the registered stage boundary, review only capture, integrity, evaluator, staffing and task-preparation feasibility with comparative rankings masked. Continue only if the registered criteria and reviewer capacity hold. No favorable-outcome-based expansion or task replacement.

Account exhaustion/outage stops new dispatch globally; record affected active attempts and unrun slots. User stop and unrecoverable failures remain endpoints. Missing slots are missing, while dispatched nondeliveries retain their distinct outcome categories. Resume under a documented environment/version boundary, not an invisible retry.

## Human review and provenance

Name the independent reviewers and confirm hours before calibration. People exposed to model identities, operator logs or comparative outcomes cannot count as blinded reviewers. The AI coordinator is not a human reviewer. Lack of staffing is a real launch blocker, not a zero-effort outcome. Use registration's capacity assumptions to reserve calibration and stage-specific review hours; actual review time may differ.

Hide model/provider, cost, runtime and session identity. Randomize/balance reviewer assignments. Reviewers time active inspection/reproduction through merge, changes-requested or cannot-assess verdicts; record familiarization/queues separately. Reviewers do not repair patches during measurement. Reproduce and adjudicate critical defects before final acceptance; style preference alone is not a functional rejection. Record recognition/blinding breaches and reviewer effects.

Include time on reviewed patches later rejected. Reuse the same blinded review when an artifact also enters the retry portfolio; do not invent a second physical review. No review data means unverified final acceptance and unknown effort, not zero cost.

An independent documentation reviewer outside the subject families must approve source selection, omissions, version coverage, extraction and absence of solution hints. The coordinator may mechanically package approved inputs; it cannot sign its own content decisions. Record curator/reviewer identities, contributions, hashes and signoffs before calibration.

## Measurement, corrections and reporting

Capture controller UTC/monotonic dispatch, first/final event and exit, endpoint snapshots, session/prompt/config IDs, tool timing/retries and native usage. Keep supervisor, worker, controller, preparation, calibration, evaluation and publication usage separate. Reconcile provider counters without adding cross-checks as extra charges. Establish input/cache/write/output/reasoning subsets before cost analysis; provider-inconsistent fields remain unresolved. Keep unavailable values missing.

Use registration's standardized price convention and report observed invoices/cache-aware/hosting/labor scenarios separately. No exclusive inference-time claim without a measurement. Show accepted-submission time separately from early failed runtime and evaluator/review latency. [ANALYSIS_PLAN.md](ANALYSIS_PLAN.md) defines paired estimates, retry selection and uncertainty.

Report all attempts, known defects, review rejections, missingness, timeout imbalance, serving differences and residual model-setting differences. No purchasing claim follows from this cohort. Optional weighted preferences cannot bypass completion. Acceptance-guided rescue is a separately registered extension. Evaluator defects suspend the affected task across arms; preserve original results and publish uniformly regraded frozen endpoints under new hashes. Contract changes create a new cohort.
