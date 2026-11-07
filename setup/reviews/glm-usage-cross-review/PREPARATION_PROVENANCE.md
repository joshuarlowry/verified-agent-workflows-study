# PREPARATION_PROVENANCE — GLM usage normalization cross-review (revision 2)

Endpoint: preparation source-review session, observed 2026-11-07T04:27:15+00:00 through
2026-11-07T04:29:58+00:00 (`date --iso-8601=seconds`). No timestamps or identities are
fabricated; only observed clock readings and controller-stated identity are recorded.

## Session identity (not a resolution claim)

- Requested model: `z-ai/glm-5.3-flash`, pinned by the controller for this session
  (harness identity `study2-glm-probe/glm`; route OpenCode/LiteLLM/OpenRouter/Relace FP4).
- Actual provider and resolved revision for this session: **null — not asserted.**
  Controller evidence will supplement invocation. No other model or subagent was invoked.
- Model calls made by this review: **0**. No calibration, scoring, or benchmark solutions.

## What was reviewed (exact source SHA-256)

| Artifact | SHA-256 |
| --- | --- |
| inputs/harness/normalize_usage.py | 6d178a013ef3c05b1f069841b659bf3d1f1c8c0d757bf78cee22d34bdce6bf69 |
| inputs/schemas/provider-usage-record.schema.json | 07b78322af0b6311b2168748bca587dbd2a1838adde9bb641c33e3ef30aa872f |
| inputs/schemas/README.md | 0cabe9e20f12ff9ee53153d857d5a990aea82c1ac7f6e6332abe3c2006085b10 |
| inputs/scripts/usage_schema_preflight.py | 07458256c33f70787823675543d755610fa8169e3855dd50c0695051479711aa |
| inputs/readiness/revision7-provider-and-accounting.json | e265a4737f6e0cb4c25e60e8881bf35c25df639fc6693d0531cb4380cecc9f5d |
| inputs/setup/reviews/terra-fixture-cross-review/FIXTURE_CROSS_REVIEW.json | 594bf8fb1a7e45696c6b777bc086f9d1220ea092e70e0e208ba2e9c3861082fd |

Independent inputs tree hash (Terra's documented algorithm, all 6 files):
`f2ad0f98f0e133a17be62cc28f8b0f45b3b3ad8565643171ffdff245c2c30edf`. This differs from
Terra's recorded `818bb233…` because the tree was restructured for revision 2
(`inputs/normalize_usage.py` relocated to `inputs/harness/`; `registration.json` absent;
`readiness/` and `scripts/` added; Terra's review file now present). Terra's
`registration.json` references could not be re-verified.

`/workspace/inputs` is a read-only mount this session: no existing input or application
file was edited. Outputs were written outside the tree:
`/workspace/USAGE_CROSS_REVIEW.json` and this file.

## Method and execution environment

Inputs were copied byte-for-byte to `/tmp/opencode/glm-usage-review/` and all execution
happened there. Two diagnostics ran:

1. **Author's probe** (`inputs/scripts/usage_schema_preflight.py`) — exit 0, 16/16 checks
   true. Its report write landed only inside the scratch copy (note N1: in-place runs
   would create a file inside the immutable inputs; relocate before qualification).
2. **Reviewer diagnostic** (mine, unapproved):
   `/workspace/diagnostics/usage-cross-review-diagnostic.py`
   (sha256 `2d159bfce66321b0a54b26ccfb2b2a0887c7d0c611a52785862711d7186c078c`, log
   `usage-cross-review-diagnostic-run.log`, sha256
   `3a0a37713140d32cc82fc5ea6f1fa1a9cf06e6d35dbc4ab8780a9779e2d856c1`). Final run: 80
   checks, exit 1, exactly one failing expectation — the U4 reproduction. Two earlier
   iterations failed from bugs in my own diagnostic (wrong dict level for the r7 usage
   payload; expected/actual argument mix-ups; a probe with mismatched response IDs) and
   were corrected before the recorded run; the source under review never changed.

Reproduction:

```
rm -rf /tmp/opencode/glm-usage-review
mkdir -p /tmp/opencode/glm-usage-review/diagnostics
cp -a /workspace/inputs /tmp/opencode/glm-usage-review/inputs
cp /workspace/diagnostics/usage-cross-review-diagnostic.py /tmp/opencode/glm-usage-review/diagnostics/
cd /tmp/opencode/glm-usage-review
python3 -B inputs/scripts/usage_schema_preflight.py       # exit 0, 16/16 true
python3 -B diagnostics/usage-cross-review-diagnostic.py   # exit 1, sole failure = U4
```

## Result summary

- **U1 (Terra, high): fixed and verified.** Record IDs hash canonical JSON tuples;
  `(run='a:b', session='c')` and `(run='a', session='b:c')` are distinct; cross-session
  same-response duplicates raise `ReconciliationError` instead of dropping or double
  charging; incomplete duplicates cannot erase known counters/cost; changed known totals
  conflict; raw snapshots and warnings retained.
- **U2 (Terra, high): fixed and verified.** Mapping gated to the single observed
  GLM/Relace registration (`glm-relace-completion-only-r7` + `relace/fp4` +
  `z-ai/glm-5.3-flash`); unequal cache aliases (0-vs-7, reversed), negative/bool/float
  counters, negative/nonfinite/bool/string costs, invalid role/phase/metadata and
  malformed nested details (now `ValueError`, not `AttributeError`) all rejected.
- **U3 (Terra, medium): declared draft limitation, correctly represented.** Null
  resolved/provider/native/parent fields and the pinned
  `provider_counters_only_native_join_and_resolution_unverified` reconciliation const
  match the README's refusal to claim `crosschecked`. No provenance integration exists to
  approve, and none is approved here.
- **Completion-only billing / reasoning preservation: consistent with immutable
  evidence.** r7 replay yields (5005/245/384/0/272 → 0.0001647555),
  (5257/13/5120/0/0 → 0.0001504987), (5279/6/5248/0/0 → 0.0001504774) with cost preserved
  verbatim and reasoning never added; Decimal recomputation of the historical 19/89/104
  case gives 0.0000087543 = reported, while completion+reasoning 0.0000183535 would
  overbill.
- **U4 (new, minor):** `deduplicate` drops `normalization_warnings` carried by a
  later-position duplicate (order asymmetry); counters/cost/snapshots unaffected;
  informational loss only. Reproduction prints `prior_pass_warning retained: False`.
- **U5 (new, low):** pathological-input exception escapes — `OverflowError` for
  huge-int cost, `KeyError`/`TypeError` for structurally malformed `deduplicate` input.
  All fail loudly; no silent corruption. Lone-surrogate `UnicodeEncodeError` is a
  `ValueError` subclass and stays within contract.

## Verdict

**Acceptable draft** for the stated limited format/normalization contract only
(normalizer, schema, README, preflight script). Not broker qualification, not launch
qualification, not scored. All-model/broker/provenance integration: **cannot assess —
deliberately unimplemented; approval withheld.**

## Limits

No broker/capture/native-join/ancestry/timing/invoice/streaming behavior was reviewed or
qualified; synthetic scratch response IDs were used for replay because the immutable
evidence contains no provider response IDs; the preflight's 7/7 alias example is the
author's synthetic mechanical case (r7 evidence shows 0/0); Terra-era
`registration.json` was unavailable; cost-conflict detection is float-exact and the
deduplicate conflict field list does not yet include `schema_version`/`counter_semantics`
(unreachable with normalize-produced records today).

Stop here: this is the review endpoint. Controller disposition, repairs (U4/U5), and any
integration work must be re-reviewed separately without self-approval.
