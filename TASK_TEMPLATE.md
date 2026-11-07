# Task contract and qualification template — canonical task template

Read current settings from [registration.json](registration.json); do not copy harness, cutoff, package or sample defaults into this template. Fill and freeze the contract before scored dispatch. Complete qualification before this task's stage begins. Empty fields are launch dependencies, not implied approvals.

## Contract and provenance

- Task ID/revision/hash; category; independent difficulty stratum; frozen stage/order.
- Baseline commit, image digest, lockfile, database fixture and local documentation hashes.
- Common MCP manifest and documentation corpus hashes; exact library versions, tool/role matrix, isolated index/cache identities and qualification signoff under [MCP_SETUP.md](MCP_SETUP.md).
- One user outcome, baseline reproduction, requested behavior and explicit non-goals.
- Actors/authentication/ownership, data boundaries, null/zero/empty/error behavior.
- Persistence/reload, compatibility, permitted edit scope and legitimate regression expectation changes.
- UI requirements including accessible roles/names/labels and keyboard behavior where applicable.
- Frozen FAQ and documented assumptions, identical for all systems.
- Author record for the baseline, reference patch, alternate valid path, each check, task contract, frozen FAQ, role prompts and worker-handoff templates: human identity/role, exact model/family/provider if used, date and artifact hash.
- Allowlisted builder and different-model cross-reviewer identities/sessions recorded; no self-approval. Disclose subject-family fixture authorship, including contracts/FAQ and coordinator prompt drafts. A fresh session is not independent model-family evidence.
- For later-stage tasks, evidence of builder blinding to earlier scored outcomes.

## Requirements, examples and sealed verification

| Requirement | Observable behavior | Public example/check | Sealed boundary/integration case | Negative control caught | Semantic UI locator or API contract |
|---|---|---|---|---|---|
| AC-01 | Required | Required where applicable | Required | Required for critical behavior | Required |

All requirements are public. Public checks are representative examples; sealed checks use new inputs or combinations from the same disclosed contract. The task measures generalization beyond visible examples, not compliance with secret requirements. Map every sealed assertion to its requirement. UI checks use `getByRole`, `getByLabel` or equivalent semantic locators; record and justify exceptions before registration.

## Environment and qualification evidence

- Dependency installation before timing; start/reset commands and isolated test database identity.
- Public targeted checks and trusted public selector predicate; regressions/build/typecheck/lint commands with reliable exit codes.
- External sealed evaluator, seeds, timezone/locale and evidence format.
- Baseline regressions pass and task acceptance fails for the expected reason.
- Complete reference passes all gates; materially different valid path also passes relevant checks.
- Negative controls demonstrate rejection of each critical omission/error.
- Baseline/reference replay in three clean instances of the frozen environment is consistent.
- Independent contract/check review and author-family provenance are signed off.
- No unresolved oracle defect, missing adapter or known flake.

## Core run records and optional review extension

- Frozen workflow deadline T; first-return/deadline/blocked endpoint and timestamp.
- Source/public-check/acceptance hashes and per-criterion accepted/rejected/unverified evidence.
- Public-check predicate result released separately from sealed results.
- Native input/output/cache/reasoning/write provenance and missing usage.
- MCP calls, errors/retries, latency, corpus/index revisions and retrieval service overhead; effective tool/corpus parity across supervisor and worker sessions.
- Human operational activity separated from blinded patch-review timing.
- Only if the human-review extension is registered: reviewer active minutes, verdicts, critical reproductions and adjudication on frozen endpoints. Otherwise record review effort and merge readiness as not measured; core machine acceptance is unaffected.
- For Gemma portfolio candidates: preregistered position and public-only selection manifest committed before sealed outcome disclosure to selector/analyst.

## Subject prompt skeleton

> Implement the single frozen task for RUN_ID against BASELINE_ID. All behavioral requirements and representative public checks are included. Plan, implement, self-review and verify the complete outcome. Sealed checks use new cases from the same requirements.
>
> You have T_MINUTES of total workflow time from dispatch. Tool/inference waits, retries and any registered worker handoffs use that same deadline. Your first complete-agent or supervisor final return freezes the endpoint. A deadline hit is not delivered; an early return passes only if independent verification accepts the artifact.
>
> Run targeted public checks and the frozen regression/build/typecheck/lint commands. Preserve regression guarantees, evaluator integrity and the registered edit scope. Use only the declared models, tools and writable paths. Report exact evidence and remaining or unverified requirements honestly.
>
> If you are the registered supervisor, you may inspect and direct the pinned Gemma worker. Gemma performs all application/test edits; you own task direction and review. Your prompts and responses are recorded separately. A worker return is a handoff within your original deadline, not a workflow endpoint.

Fill role mechanics, permissions, deadline and hashes before use. This template has not been dispatched.
