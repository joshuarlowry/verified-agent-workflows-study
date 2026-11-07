# Preparation Provenance

## Review Scope
Cross-review of runtime preparation helpers for study-local container signal repair.
Model: Gemma 4 31B (Pinned)
Date: 2026-11-07

## Artifact Verification
- **AppArmor Profile**: `study2-agent.profile` verified against `profile-source.json` and mechanical diagnostics.
- **Build Helper**: `build_candidate_image.py` verified for dependency pinning and image integrity.
- **Replay Helper**: `replay_candidate_baseline.py` verified for instance isolation and security constraints.
- **Diagnostic Helper**: `signal_preflight.py` verified for fault isolation and zero-model-call control.
- **Endpoint Recorder**: `record_preparation_endpoint.py` verified for sanitization and identity cross-checking.

## Findings Summary
- **Source Correctness**: All helpers implement the described logic without visible defects.
- **Consistency**: Claims regarding signal failure reproduction and repair are supported by provided measurement records (`signal-preliminary.json`, `r1-container-runtime-signal-repair.json`).
- **Isolation**: The candidate profile maintains the security posture of the default (zero capabilities, NNP, seccomp) while specifically permitting the same-profile stacked signal communication.
- **Credential Handling**: No credentials are stored in source; API keys are read from restricted host paths.

## Verdict
The runtime preparation helpers and the candidate AppArmor profile are correct and consistent with the study requirements.

## Evidence Limits
Review conducted in a read-only construction view. No live image builds or container executions were performed. Verification relied on source analysis and provided measurement outputs.
