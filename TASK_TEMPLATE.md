# Task contract template — draft

No field marked required may remain unresolved at registration. This template is not itself a qualified task.

- **Task ID / revision / hash:** required
- **Baseline commit / image digest / lockfile hash:** required
- **Task category:** required
- **One-sentence user outcome:** required
- **Observed baseline behavior and reproducible example:** required
- **Requested behavior:** required; describe public behavior, not a reference implementation
- **Non-goals:** required
- **Actors, ownership and authentication rules:** required
- **Input/domain boundaries, null/zero/empty/error behavior:** required
- **Persistence, reload and compatibility behavior:** required
- **UI interaction and accessibility requirements, if applicable:** required
- **Permitted edit scope / legitimate baseline expectation changes:** required
- **Frozen FAQ:** required; no individualized product coaching

## Acceptance map

| Requirement ID | Observable criterion | Public examples/checks | Independent acceptance check | Negative control rejected | Evidence artifact |
|---|---|---|---|---|---|
| AC-01 | Required | Required | Required | Required | Required |

Every requirement must map to a check or a predeclared review procedure. A sealed check may use different data, but not an undisclosed behavioral requirement. Use public API/UI contracts rather than undocumented helper names.

## Trusted commands and environment

- Dependency installation before timing: required
- Start app/API/database and reset fixtures: required
- Public targeted checks: required
- Existing regressions, build, typecheck, lint: required
- External independent evaluator: required
- Seeds, ports, locale/timezone and test database identity: required
- Which failures mean rejected, unverified, infrastructure interruption or protocol violation: required
- Evaluator outputs: criterion ID, status, exit code, source/evaluator hash and evidence location

## Qualification evidence

- Baseline regression checks pass; task acceptance fails for the intended reason.
- Complete reference solution passes every gate on three fresh environments.
- Independently reviewed alternate valid implementation passes relevant checks.
- Negative controls catch each critical missing/incorrect behavior.
- Contract, checks and behavior reviewed independently of their author.
- Reviewer identity/role, human versus AI contribution, timestamp and signoff recorded.
- No unresolved oracle defect, missing adapter, unknown critical behavior or known flake.

## Subject prompt skeleton

> You are the complete implementation agent for RUN_ID, or the registered supervisor if this configuration explicitly assigns that role.
>
> Implement the single task in the attached frozen contract against BASELINE_ID. All behavioral requirements and public checks are included. Plan the work, implement, self-review and verify the complete requested outcome. No other task or run is in scope.
>
> Run the targeted checks and the frozen final regression/build/typecheck/lint commands. Keep reliable exit codes. Do not remove regression guarantees, weaken checks, access other runs or change the evaluator. Use only the registered models, tools and writable paths.
>
> Continue through your own verification and repair work until the contract is satisfied or you reach a concrete blocker. Your first final return is a recorded endpoint; it is not a request for an operator to choose the next step. Report exact evidence and any remaining or unverified requirements honestly.
>
> A supervisor may review and direct its pinned worker but may not edit application/test code or supply a complete replacement implementation. Only the worker edits application code and tests. Worker handoffs are not supervisor final returns. All supervisor/worker prompts and responses are logged separately.

Role-specific launch mechanics, allowed paths and database authorization must be filled and hashed before use. This skeleton is not a dispatched prompt.
