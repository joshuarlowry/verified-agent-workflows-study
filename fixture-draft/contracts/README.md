# Workboard Lab — Task Contracts (DRAFT)

Status: **DRAFT — authored, not qualified.** These contracts were drafted by
the preparation-phase fixture builder. They have NOT been cross-reviewed, no
reference implementations exist yet, and no sealed tests exist yet. Do not
treat any contract here as validated or solvability-confirmed. Reference
implementations and sealed tests will be created and cross-reviewed in a
separate phase after these contracts are reviewed.

## Authorship disclosure

All three study models build and cross-review fixtures in fresh sessions,
and they are **not independent model families**. The user explicitly waived
the family-exclusion requirement for this study but disclosure remains
mandatory: there is no independent-family authorship here; every artifact in
this workspace (baseline, contracts, docs) was authored by
`z-ai/glm-5.3-flash` (this session) and will be reviewed by same-family
models. Review findings must therefore be checked on substance, not on
authorship independence.

## How to read a contract

Each task is a **single coherent incremental behavior** on top of the frozen
baseline (`baseline/docs/baseline-contract.md`). Sections:

- **Baseline behavior** — what exists today (normative, from the baseline
  contract).
- **Requirement** — the one behavior this task adds. Everything the agent
  must implement is derivable from this + the examples.
- **Public examples** — concrete API/CLI/UI traces with exact expected
  outcomes.
- **Boundaries & non-goals** — explicitly out of scope; implementing them is
  a scope violation, not extra credit.
- **Compatibility expectations** — baseline guarantees that must keep
  holding (`npm run check:full` stays green).
- **Ownership** — files/areas the implementer owns; touchpoints they may
  modify; things they must not touch.
- **Acceptance mapping** — requirement → observable check.

Calibration tasks (C1–C4) are small end-to-end shakedown tasks for pipeline
calibration. Scored tasks (S01–S15) are the graded variety. Both are DRAFT.

## Index

| ID | Title | Variety |
|---|---|---|
| C1 | Workspace item counts | full-stack small |
| C2 | Item list sort toggle | API param + UI |
| C3 | Item share link (clipboard + deep link) | navigation/state |
| C4 | Remember last workspace | client persistence |
| S01 | Input validation hardening (trim + limits + field errors) | validation |
| S02 | Archive and restore work items | archive/restore |
| S03 | Stable cursor pagination | pagination |
| S04 | Transactional JSON import | import transactionality |
| S05 | High-fidelity JSON export | export fidelity |
| S06 | Destructive-action permissions | ownership |
| S07 | Failure-safe editing (draft recovery) | recovery after failed saves |
| S08 | Due-date semantics (tz-safe calendar) | calendar dates |
| S09 | Optimistic concurrency (409 + conflict UX) | version conflicts |
| S10 | Workspace-switch guard | dependent UI state |
| S11 | Multi-select bulk status update | dependent UI state / batch |
| S12 | Item activity history | audit/persistence |
| S13 | Owner-managed memberships | ownership/roles |
| S14 | Workspace overview summary | aggregation |
| S15 | Keyboard quick-add and focus management | a11y/UX |

Cross-task advisories (independent on the baseline, but adjacent): S02/S03
(list surface), S04/S05 (JSON formats, intentionally incompatible), S06/S13
(authorization surface), S07/S10 (unsaved-input surfaces), S11/S12
(multi-change logging).
