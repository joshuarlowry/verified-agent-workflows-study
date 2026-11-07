# Preparation work log

Current method and gates are canonical in [registration.json](../registration.json). No calibration/scored workflow has been dispatched.

## Started after the cross-review authorization

- **GLM fixture builder:** fresh OpenCode session through LiteLLM/OpenRouter, pinned to Relace FP4. Writes a new baseline, draft task contracts/FAQ and documentation source inventory. Prior experiments and controller logs are outside its filesystem view. Output remains private and unqualified until its endpoint and cross-review. [Dispatch prompt](prompts/glm-fixture-builder.txt).
- **Terra protocol/role-prompt cross-review:** separate fresh OpenCode session through LiteLLM/OpenRouter/Azure, high reasoning. Reads immutable protocol inputs, reports findings and drafts role prompts for later different-model review. It cannot approve its own new prompts. [Dispatch prompt](prompts/terra-preparation-review.txt).
- **Resource preflight:** rootless Podman could not enforce cpuset. A local rootful container alternative enforced two CPUs and an 8 GiB memory limit with no network and no host home mounted. The generic solo/concurrent probe passed its preliminary enforcement/contention checks. [Raw measurements](resource-preliminary.json), [probe script](../scripts/resource_preflight.py). Real application, inference-rate and complete subject-isolation qualification are still pending. This is not a completed lane signoff.

These are construction/review roles, not new evaluation treatments. Only the authorized Gemma, GLM and Terra model IDs may be launched. The existing GPT-family coordinator writes protocol/harness instructions and logs mechanical actions; model-authored application/contract/check artifacts carry their own attribution. Reports will disclose the benchmark's dependence on the evaluated model families.

Raw native events, stderr, gateway/provider usage and process metadata remain outside subject access. Each first construction/review endpoint is preserved; subsequent preparation revisions will have separate prompts, timestamps and evidence. No preparation result is silently counted as scored success.

## First review endpoint and transport probe

Terra returned its first protocol cross-review endpoint, with an explicit draft/no-launch-signoff status. Its [unchanged report and role drafts](reviews/terra-protocol-review/CROSS_REVIEW.json) are preserved; these reflect its input snapshot and are not current canonical settings. Gemma is cross-reviewing the Terra-authored drafts in a separate session. No authored prompt is self-approved.

The [synthetic transport test](transport-preliminary.json) passed a real network-disabled container → loopback bridge → mounted Unix socket → host proxy → synthetic upstream round trip, stream/usage capture, model/provider-override rejection and preservation of budget-refusal status. It made zero model calls. The [transport helpers](../harness/) remain preparation candidates; real OpenCode, Context, worker broker and full application/evaluator isolation are not yet qualified.

Gemma returned its first cross-review endpoint: the three subject prompts were labeled acceptable drafts; the broker draft needs an explicit usage schema. The original report is preserved. Its self-reported timestamp is inconsistent with controller UTC, and helper source hashes were left `not_computed`; those provenance gaps are not silently repaired. Controller measurements and hash supplements are separate evidence. No broker/runtime signoff is granted.

## Usage format follow-up

The coordinator added a [draft final-provider usage schema](../schemas/provider-usage-record.schema.json) and [normalizer](../harness/normalize_usage.py) in response to Gemma's broker-schema finding. The mechanical probe preserves the observed GLM completion/reasoning mismatch without overbilling, does not double cache-write aliases or repeated snapshots, and retains missing counters as null. [Probe result](usage-schema-preliminary.json). Different-model review and broker integration remain pending; this does not silently close Gemma's original finding.

## First fixture and cross-review

GLM returned its [first source-only fixture endpoint](../fixture-draft/README.md), including the baseline and 19 draft task contracts. [Source manifest](glm-builder-first-endpoint.json) preserves all 68 source paths/hashes; generated dependencies, caches, databases and browser outputs are excluded from the public export. The controller independently replayed the builder-authored public full-check command with exit 0; this is not an independent task acceptance suite or three-clean-container qualification.

[Terra's fixture cross-review](reviews/terra-fixture-cross-review/FIXTURE_CROSS_REVIEW.json) reproduces test/bootstrap behavior and identifies a stale cross-workspace data bug, contradictory examples/policies and usage-normalizer edge cases. The first builder tree is unchanged. A new GLM preparation revision is repairing application/contract/FAQ/source issues. No reference/sealed tests or scored runs exist yet. Normalizer revision 2 addresses collision, incomplete-snapshot, alias and validation findings; its adversarial mechanical tests pass, but cross-review and full integration remain pending.

[Context mechanics](context-preliminary.json) now pass in a network-disabled container with a read-only generic archive. [The initial cleanup/timing issue](context-cleanup-incident.json) is preserved separately. This does not qualify the application-version documentation corpus. CPU preflight assigns equal CPU masks; it does not reserve exclusive host cores or complete app/inference contention qualification.

## Repair R1 and limited usage review

GLM returned a [separate R1 source endpoint](../fixture-revision-r1/REPAIR_PROVENANCE_R1.md), preserving the first fixture. Its full public check passed 11 unit, 34 API and 18 browser tests. [The source manifest](glm-repair-r1-endpoint.json) and invocation record preserve this construction revision; a new Terra session is cross-reviewing it. This is not task acceptance or calibration.

[GLM's usage cross-review](reviews/glm-usage-cross-review/USAGE_CROSS_REVIEW.json) labels revision 2 an **acceptable limited draft**, verifies U1/U2 repairs, and explicitly withholds broker/all-model/provenance approval. It also reports U4 (later-duplicate warning retention) and U5 (exception types on pathological inputs); both remain known draft limitations. Reviewer diagnostics and their nonzero exit on U4 are preserved, not presented as clean tests.

The [real CLI synthetic round trip](opencode-transport-preliminary.json) passed through the network-disabled container/Unix gateway with two native model steps and a shell tool result, using zero model calls. [The first probe](opencode-transport-initial.json) failed with unexpected synthetic-call ordering/counts and a cleanup signal error. It omitted an explicit title, allowing an extra title-generation path; explicit titles and container-owned cleanup produced a clean round trip. The exact first-call ordering was not retained in that initial record. The successful result still does not qualify real models, corpus or the broker.

An offered-tool audit found the current native tool is `subagent`, whereas earlier preparation policy named `task:*`. Captured native events show no delegation calls in the completed preparation sessions; that audit does not prove shell-level absence of all possible delegation. A [forced synthetic delegation test](opencode-delegation-preliminary.json) now proves `agents.build.permissions` denying the `subagent` action removes it from the catalog and rejects a forced call, with only one native session. [The initial assertion](opencode-delegation-initial.json) incorrectly expected a permission-worded error; it actually received “No tool named” because the tool was removed. Both records are retained. Subsequent construction config uses the effective native rule; final role parity and shell/process restrictions remain separate qualification gates.

Gemma has begun a fresh official-document snapshot/Context archive construction session, using only the baseline and source inventory. It has no task contracts, solutions or comparative outcomes. A different authorized model must review its corpus; no application corpus is yet qualified. Preparation sessions can overlap, so their runtimes are not controlled model-performance comparisons.
