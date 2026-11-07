# Current preparation status

Use [registration.json](../registration.json) for the study design and launch gates, and [status.json](status.json) for the current preparation state. This directory contains current supporting evidence, not competing planning versions. Reports retain original session/revision identifiers and are unchanged audit artifacts.

- **Application:** the one current source tree is [fixtures/baseline](../fixtures/baseline). GLM cross-review found it consistent; three clean container replays passed.
- **Task contracts and FAQ:** current copies are under [fixtures](../fixtures). Reference solutions, materially different alternatives, sealed acceptance checks and negative controls still need qualification.
- **Documentation:** the rebuilt corpus passed source/extraction cross-review with conditions. Actual seven-role Context integration and redistribution review remain open. Raw source material stays private.
- **Harness:** synthetic transport/Context and physical isolation checks have passed within their stated limits. Actual supervisor-worker integration, complete usage/endpoint handling and concurrent-lane qualification remain open.

**Current preparation:** [Run status](RUN_STATUS.md) updates automatically at dispatch and job endpoints. Gemma has returned a source-focused review of the C1 evaluator; its [limitations](evaluator-review.json) leave task qualification open. [Transport diagnostics](transport-diagnosis.json) did not reproduce Terra's earlier failure. One explicitly recorded identical-prompt harness retry is running with raw upstream capture; this does not establish a fix. C1 reference and separately authored alternative builders are queued sequentially, conditional on that retry returning normally. A failed dependency halts that queue. The original failed endpoint is preserved.

**No calibration or scored run has started.** Current materials are not launch-qualified.

Superseded drafts and failed setup iterations are removed from the current tree. Their [immutable audit snapshot](https://github.com/joshuarlowry/verified-agent-workflows-study/tree/e1750c4ddcf7614d179e3510303a1fd8e13f001d) and the [private artifact backup](https://github.com/joshuarlowry/verified-agent-workflows-artifacts) preserve provenance. Earlier reports may name historical paths; use that snapshot when resolving them. Source files were relocated without changing application, contract or FAQ content.
