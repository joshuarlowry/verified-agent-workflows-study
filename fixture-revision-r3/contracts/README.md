# Workboard Lab — Task Contracts (DRAFT, revision R3)

Status: **DRAFT — authored, repaired, not qualified.** These contracts were
drafted by the preparation-phase fixture builder, revised in repair session
R1 (see `../REPAIR_PROVENANCE_R1.md` and `../REPAIR_DISPOSITIONS_R1.json`),
and revised again in repair sessions R2 and R3 (see the corresponding
`../REPAIR_PROVENANCE_R2.md`, `../REPAIR_DISPOSITIONS_R2.json`,
`../REPAIR_PROVENANCE_R3.md` and `../REPAIR_DISPOSITIONS_R3.json`). R3 has
not yet received the required different-model cross-review; no reference implementations
exist, and no sealed tests exist. Do not treat any contract here as
validated or solvability-confirmed. Reference implementations and sealed
tests will be created and cross-reviewed in a separate phase after these
contracts are reviewed.

## Authorship disclosure

The three study-model families — Gemma, GLM and Terra — are the **subject
models of this benchmark**: they construct fixtures, draft and revise task
contracts, and cross-review each other's work in fresh, separately recorded
sessions. This workspace's baseline and contracts were authored by the GLM
session (`z-ai/glm-5.3-flash` via OpenCode/LiteLLM/OpenRouter/Relace FP4);
R3 was authored by Terra (harness identity `study2-terra-fixture-review/terra`,
requested `openai/gpt-6.1-terra` via Azure, high reasoning; exact upstream
routing requires controller evidence). The usage schema and normalizer outside this workspace were authored by the
coordinator. Because reviewers and authors belong to the subject-model
families themselves, review evidence here is **not independent-family
evidence**; the user waived family exclusion but disclosure remains
mandatory. Review findings must be checked on substance. No artifact claims
that the participating models are a single model family, and no artifact
claims independent qualification.

## Execution model (settled at revision R1)

**Every task runs against a freshly reset baseline.** Before each scored or
calibration task, the baseline is reset to its frozen state
(`npm run db:reset` on a disposable SQLite file; fresh checkout of the
baseline tree). No task may assume another task's changes, fields, or
endpoints: each contract is an **independent single-baseline increment**.
Combined-task behavior is undefined and must not be tested by any
acceptance check. Final corpus packaging remains a coordinator decision, but
the reset-per-task policy above is the preparation-phase default and is
reflected in every contract's boundaries.

## How to read a contract

Each task is a **single coherent incremental behavior** on top of the frozen
baseline (`baseline/docs/baseline-contract.md`). Sections:

- **Baseline behavior** — what exists today (normative, from the baseline
  contract).
- **Requirement** — the one behavior this task adds. Everything the agent
  must implement is derivable from this + the examples.
- **Public examples** — concrete API/UI traces with exact expected outcomes.
- **Boundaries & non-goals** — explicitly out of scope (including disclosed
  edge-case boundaries); implementing them is a scope violation, not extra
  credit.
- **Compatibility expectations** — baseline guarantees that must keep
  holding (`npm run check:full` stays green).
- **Ownership** — files/areas the implementer owns; touchpoints they may
  modify; things they must not touch.
- **Acceptance mapping** — requirement → observable check.

Calibration tasks (C1–C4) are small end-to-end shakedown tasks for pipeline
calibration. Scored tasks (S01–S15) are the graded variety. Both are DRAFT.

## Baseline test edits — uniform precedence rule (settled at R1)

Baseline tests are regression guards. The default rule is: **do not change,
delete, or weaken them; add new tests alongside.** A task contract may
override this only for assertions that the task's requirement makes
obsolete, under these constraints:

1. **Enumerated, not general.** The contract must identify the affected
   test file(s) and assertions or selectors by exact site or exhaustive
   predicate (e.g. every workspace option-label selection in named files).
   Anything not enumerated stays untouched.
2. **Assertion/selector-only migrations.** A permitted edit may only update an
   expected string/value/shape or equivalent selector that the task changes, or replace a test
   whose flow the task makes impossible — with an equivalent-coverage test
   named in the contract. Tests must never lose behavioral coverage.
3. **Documented in the task notes.** The implementer records every
   migrated assertion; `npm run check:full` must exit 0 with the migrated
   expectations.
4. **The baseline contract stays frozen.** Task contracts define the new
   behavior; the baseline contract is not edited by tasks.

Contract-specific overrides always win over this general rule for their
enumerated scope; this rule fills the gaps.

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

## Overlap advisories (shared primitives, not duplicate tasks)

Contracts are independent single-baseline increments; several touch the same
baseline primitives. The overlap is deliberate and is **not** proof of
duplicate tasks; no model-favoring selection follows from it.

- **C1 / S14** both count items: C1 adds per-workspace `openItemCount` on
  the workspace/me responses; S14 adds a separate summary endpoint and
  overview panel (all three statuses + last activity). If both were ever
  combined, `byStatus.open` must equal `openItemCount` (same definition:
  `status = 'open'`) — but per the reset policy they are never combined.
- **S01 / S08 / S09** all touch PATCH semantics: S01 owns title/notes
  validation, S08 owns dueDate validation, S09 adds an optional version
  hint. Each forbids touching the others' fields.
- **S07 / S10** both concern unsaved input: S07 covers reload/crash
  survival via sessionStorage; S10 covers the switch moment. Independent by
  trigger and store.
- **S02 / S03** both touch the item list surface (filter param vs cursor
  params). Each states the other is out of scope.
- **S06 / S13** both concern authorization: S06 restricts destructive item
  actions; S13 changes who members are. S06's rule applies to whoever is a
  member at the time.
- **S04 / S05** are related JSON formats that are deliberately incompatible
  (import does not consume export).
- **S11 / S12** both create multi-change behavior; S11 bulk updates are
  explicitly out of S12's recording scope.
- **C2 / C4 / S15** all add client state near the workspace selector/sort;
  none persist or interact (C2 explicitly excludes persistence, C4 owns
  localStorage, S15 owns shortcuts).
