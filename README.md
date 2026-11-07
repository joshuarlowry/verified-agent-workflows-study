# Verified Agent Workflows — Study 2

**A draft study plan. No experimental runs or results yet.**

We want to learn which coding workflow reliably delivers an accepted software change, and what that delivery costs in model usage, elapsed time and human effort. Verified completion is the gate; a fast, cheap, incomplete return is not successful delivery.

This is the public home for the follow-up to the [Minutes Agent Workflow Study](https://joshuarlowry.github.io/minutes-agent-workflow-study/). The earlier study remains a separate exploratory pilot.

## Read the plan

- **[Study protocol](PROTOCOL.md)** — research question, configurations, task design, acceptance gates, controls, measurement and reporting.
- **[Task contract template](TASK_TEMPLATE.md)** — the requirements and validation evidence each task needs before registration.
- **[Draft registration](registration.json)** — explicit unresolved fields; currently marked `draft_not_launchable`.

## Proposed experiment

| Item | Proposal |
|---|---|
| Application | New small application with real UI, HTTP API and local test database |
| Models | Gemma 4, GLM and Terra through their registered harnesses |
| Configurations | Gemma alone; GLM alone; Terra alone; Terra supervising Gemma; GLM supervising Gemma |
| Calibration | Two separate tasks across all five configurations: 10 unscored runs |
| Scored collection | Ten tasks × three repetitions × five configurations: 150 proposed runs |
| Completion | All applicable frozen acceptance, integration, regression and integrity gates pass |
| Spending policy | No imposed dollar or token budget |

These are proposed design choices, not a claim that the fixture, model availability or acceptance system has been verified. The application baseline, test packs, reviewers and run schedule must be qualified and frozen before registration. The sample size is not a spending cap or a statistical power claim.

## Next milestone

Prepare and independently qualify the application fixture and two calibration tasks. Prove that the evaluator rejects unchanged or incomplete implementations and accepts valid solutions. Verify capture, isolation and model routing before considering scored dispatch.

GLM supervising Terra and reciprocal reviewer arrangements are possible later treatments, not part of the five-configuration core.

## Public and private materials

This repository holds the public protocol, registration history and eventual sanitized reports. Keep credentials, raw private logs, unreleased reference solutions and sealed acceptance implementations in a separate restricted control environment. Publication of a plan does not authorize production access or start experiments.

## Provenance

The plan was drafted by an AI coordinator under human direction. The human selected a new application as the study base. This draft has not yet received the independent task/acceptance review required by its protocol. The original draft was recorded in the [first study repository](https://github.com/joshuarlowry/minutes-agent-workflow-study/tree/6dc7946/docs/study-2); this repository is the active home for Study 2.
