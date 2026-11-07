# Current preparation status

Use [registration.json](../registration.json) for the study design and launch gates, and [status.json](status.json) for the current preparation state. This directory contains current supporting evidence, not competing planning versions. Reports retain original session/revision identifiers and are unchanged audit artifacts.

- **Application:** the one current source tree is [fixtures/baseline](../fixtures/baseline). GLM cross-review found it consistent; three clean container replays passed.
- **Task contracts and FAQ:** current copies are under [fixtures](../fixtures). Reference solutions, materially different alternatives, sealed acceptance checks and negative controls still need qualification.
- **Documentation:** the rebuilt corpus passed source/extraction cross-review with conditions. Actual seven-role Context integration and redistribution review remain open. Raw source material stays private.
- **Harness:** synthetic transport/Context and physical isolation checks have passed within their stated limits. Actual supervisor-worker integration, complete usage/endpoint handling and concurrent-lane qualification remain open.

**Current preparation:** [Run status](RUN_STATUS.md) updates automatically at dispatch and endpoints. Gemma returned a source-focused C1 evaluator review; its [limitations](evaluator-review.json) leave qualification open. [Paired transport captures](transport-diagnosis.json) isolate the premature-stop bug to LiteLLM's substring check for the SSE marker. The [study-only repair](../harness/litellm_compatibility/README.md) passed iterator, exact captured-content replay, startup-guard and real Terra/OpenCode file checks. GLM is cross-reviewing it. A separate preparation batch is gated on an acceptable review and unchanged passing repair: Terra harness construction, then Terra C1 reference and Gemma alternative construction, sequentially. No failed endpoint is replaced. The earlier unpatched retry and its dependent queue remain stopped and preserved.

**No calibration or scored run has started.** Current materials are not launch-qualified.

Superseded drafts and failed setup iterations are removed from the current tree. Their [immutable audit snapshot](https://github.com/joshuarlowry/verified-agent-workflows-study/tree/e1750c4ddcf7614d179e3510303a1fd8e13f001d) and the [private artifact backup](https://github.com/joshuarlowry/verified-agent-workflows-artifacts) preserve provenance. Earlier reports may name historical paths; use that snapshot when resolving them. Source files were relocated without changing application, contract or FAQ content.
