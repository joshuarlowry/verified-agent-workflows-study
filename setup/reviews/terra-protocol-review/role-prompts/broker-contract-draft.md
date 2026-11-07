# DRAFT broker contract — not implemented or qualified

`{{BROKER_COMMAND}}` is a placeholder, not an executable interface. Its syntax, transport and implementation must be specified and independently cross-reviewed under the registered different-authorized-model policy before freeze. No handoff or adapter qualification is asserted here.

## Required inputs

- Parent run, supervisor session and authenticated role; task/baseline and isolated workspace identifiers; worker session identifier or a request to create one. All path and identity resolution is controller-owned, not trusted from free text.
- Frozen public task and FAQ, edit/protected scope, allowed tools/resources, public check/feedback interfaces and permitted local service/network policy, with hashes or versioned references. No sealed content, private logs, credentials or sibling-run paths.
- Registered pinned Gemma requested/resolved model, provider/tag/precision, settings and no-fallback policy by immutable manifest reference; approved common adapter/MCP configuration. No price or model defaults are embedded here.
- Bounded work request and allowed public feedback, worker prompt version/hash, parent dispatch time, absolute deadline and trusted remaining-time source. A worker request cannot extend or reset the parent's deadline.

## Required behavior and outputs

- Admit only the registered supervisor-to-Gemma handoff; enforce worker permissions and the parent's isolated workspace, services and deadline at the process boundary. Stop/reject handoffs at the deadline or on registered stop; terminate active worker/tool processes and prevent late writes to the frozen endpoint. Define and test snapshot/termination ordering and races before qualification.
- Return worker session and call IDs, status (including failure, timeout or interruption), event timestamps, public response and public check results if any, and an auditable change summary or patch reference within the same workspace. No sealed evaluator output is returned. A worker final response is a handoff; only supervisor final return is the workflow endpoint.
- Capture supervisor and worker prompts, messages, tool calls/results, retries, configuration inheritance, timing and session ancestry in access-controlled controller logs. Capture raw gateway/provider usage per call including input, output, cache/write/reasoning fields when present, provider cost, native adapter fields and missingness; preserve source and units. Correlate all IDs including retries without counting cross-checks as new calls. Do not derive GLM billed output from an unqualified native split. Reconcile and map counters under registration before cost analysis.
- Record requested and actual resolved model/provider/tag/precision when available, including errors and fallback attempts; reject unregistered fallback and signal drift for global dispatch stop. Treat unavailable actual resolution as missing, not verified.
- Return actionable mechanical errors without private diagnostics or quality hints. No controller choice of implementation task or rescue after final return. Specify worker session continuation/freshness, concurrency and cancellation semantics; never allow a detached worker to outlive the frozen endpoint.

## Qualification before use

A different authorized model reviews this draft and later substantive revisions; fresh sessions are cross-review, not independent-family qualification. Implement and test the actual interface through the pinned OpenCode/LiteLLM path. Verify exact provider pins and no fallback, common tool/corpus inheritance, physical access restrictions, parent/worker IDs and prompt hashes, session continuation, deadline/stop races and atomic snapshot behavior, public-only feedback, error/retry records and raw/native usage capture and reconciliation. Replay direct and supervised paths with equal available public capabilities and isolation. Save hashes, authorship, review and preflight evidence; unresolved failures block calibration. No human patch reviewer is required for core qualification.
