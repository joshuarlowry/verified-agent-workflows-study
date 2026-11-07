# Preparation provenance — cross-review and drafts

## Session and settings

- UTC review timestamp: 2026-11-07T03:15:25Z (local `date -u`). Preparation only; not a scored treatment.
- User-requested identity: Terra, `openai/gpt-6.1-terra`, OpenCode → LiteLLM → OpenRouter → Azure, high reasoning. The registration lists resolved revision `openai/gpt-6.1-terra-20261026`, but this session did **not** independently verify its actual resolved revision, upstream route, provider pin, fallback policy or effective reasoning setting.
- Harness-provided model metadata: name `Terra Azure High`, provider ID `study2-terra-review`, model ID `glm`. These could be internal aliases; they do not establish the upstream identity. Session ID and settings hash were not exposed in the available metadata. Qualifying signoff requires invocation/session evidence and actual route/settings verification. No additional model or subagent was invoked.
- The user identifies existing coordinator protocol/template drafts as authored by the OpenAI GPT-family coordinator currently `gpt-6.1-sol`. That is disclosed authorship, not independent qualification. The registration records current `TASK_TEMPLATE.md` authorship and notes earlier per-edit attribution is unknown. This review does not invent any missing historical attribution.

## Scope and authorship

Reviewed the seven immutable files in `inputs/`: protocol, registration, task template, builder handoff, application/docs plan, MCP setup and analysis plan. Reviewed their stated consistency, completion criteria, leakage boundaries, role neutrality, usage/time accounting and authorized cross-review methodology. Did not modify them. Did not inspect application code or sealed task answers; none were required for this document review. References to readiness/history outside the supplied input bundle were not accessed.

Authored new `CROSS_REVIEW.json`, the three `role-prompts/*.md` subject drafts, and `role-prompts/broker-contract-draft.md`; this provenance file was also authored in this session. The new substantive prompts and broker contract are **not approved** and require a different authorized model's review in a fresh session before freeze. The review is not approval of the author's own drafts. The existing inputs remain drafts where indicated, and the broker is not implemented or qualified. No app/fixture/contract/FAQ/evaluator was authored here.

Authorized model families may build and cross-review fixtures; another authorized model in a fresh session reviews each substantive artifact. Such cross-review is not independent-family authorship and does not eliminate shared model priors or training bias. Human review is optional, not a core patch-acceptance gate. This review cannot itself count toward a qualifying signoff until actual reviewer identity and author-difference evidence are verified.

## Findings and status

`CROSS_REVIEW.json` contains 14 findings, exact file/line paths, proposed minimal fixes and unresolved assumptions. Principal blockers: missing full adapter/provider/broker and raw-usage qualification; unbuilt/unqualified fixtures, corpus and evaluator controls; pending different-model review of treatment drafts; unproven physical isolation and endpoint race handling; unresolved invocation evidence; and pending lane/schedule/registration evidence. Terminology, replay scope, later-stage blinding and endpoint status schema are recorded separately as improvements before their relevant freeze. No finding implies an extra model or mandatory human patch reviewer.

Draft prompt design uses common public contract/FAQ, tools and checks, with registered role-specific edit and delegation limits, one overall deadline, and first-final-return semantics. Broker commands are explicit placeholders; no working handoff is represented. Physical restrictions and termination must be implemented and tested externally, not trusted to prompt instructions.

## Exact checks performed

1. Listed `/workspace` and enumerated `/workspace/inputs` with local file tools. Read all seven supplied input files in full; no app or sealed data read.
2. `sha256sum inputs/*` — generated the seven SHA-256 values recorded per artifact in `CROSS_REVIEW.json`. In particular, `inputs/TASK_TEMPLATE.md` produced `38b66858c4433805dab5f16d398b5cb7b2de37ef46127279e533b84876680a3e`, matching its registration author record.
3. `sha256sum role-prompts/*.md` — generated the four draft hashes recorded in `CROSS_REVIEW.json`.
4. `python3 -c 'import json,pathlib,hashlib; p=pathlib.Path("CROSS_REVIEW.json"); d=json.loads(p.read_text()); errors=[]; [errors.append(a["path"]) for a in d["artifacts"] if hashlib.sha256(pathlib.Path(a["path"]).read_bytes()).hexdigest()!=a["sha256"]]; print("JSON parse: PASS"); print("artifact SHA-256 matches:", "PASS" if not errors else "FAIL " + repr(errors)); print("artifacts:",len(d["artifacts"]),"findings:",len(d["findings"])); raise SystemExit(bool(errors))'` — `JSON parse: PASS`, `artifact SHA-256 matches: PASS`, `artifacts: 11 findings: 14`. This validates JSON syntax and listed hashes, not substantive correctness.
5. `sha256sum CROSS_REVIEW.json role-prompts/*.md inputs/*` — reconfirmed the listed artifact hashes. The review JSON was subsequently updated to include this provenance file's hash; the resulting review hash can be checked externally when packaged. No file is required to hash itself.

No network, database access, migrations, deploy/push, calibration or model scoring. No public application checks were run because this was a document-only preparation session and no application was inspected. No independent confirmation of the referenced transport probes, runtime pins or readiness evidence is claimed.
