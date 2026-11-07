# PREPARATION_PROVENANCE.md

## Review Context
- **Reviewer**: Gemma 4 (google/gemma-4-31b-it)
- **Target**: Terra's broker prototype (Synthetic Candidate)
- **Session**: Fresh preparation cross-review session
- **Scope**: Limited synthetic contract, source code, and mock tests.

## Evidence Base
- **Immutable Inputs**:
    - `/workspace/inputs/original-broker-contract.md`
    - `/workspace/inputs/registration.json`
    - `/workspace/inputs/broker-candidate/` (broker.py, CLI_CONFIG_CONTRACT.md, gemma-broker, tests/)
- **Diagnostic Execution**:
    - Worktree created at `/workspace/diagnostics/broker-candidate`.
    - Path fix applied to `tests/test_broker.py` (line 19) to resolve `registration.json` location.
    - Test Suite Result: 12/12 tests passed.

## Constraints Observed
- No real model calls, subagents, or worker calls were performed.
- No modifications were made to immutable inputs.
- No replacement broker or app solutions were implemented.
- Real OpenCode/container integration gates were explicitly distinguished from synthetic source behavior.
