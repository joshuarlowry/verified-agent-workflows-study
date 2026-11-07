# Terra through OpenRouter: readiness check

**Passed on 2026-11-07 UTC (November 6 local time).** The exact requested model works through OpenCode → LiteLLM → OpenRouter → Azure. This is a disposable transport check, not calibration, a coding benchmark, or evidence of task completion. The study registration remains unchanged.

## Configuration

| Setting | Verified value |
|---|---|
| Requested OpenRouter model | `openai/gpt-6.1-terra` |
| Resolved model in two OpenRouter generation records | `openai/gpt-6.1-terra-20261026` |
| Provider | Azure, pinned; regional variants excluded |
| LiteLLM alias | `experiment-terra-6-1` |
| OpenCode selector | `litellm-terra-experiment/terra-implementation` |
| Versions | LiteLLM 1.103.3; OpenCode 2.2.5 |
| Reasoning | `high` configured in LiteLLM; reasoning usage observed |
| Routing | Fallbacks disabled, parameter support and zero data retention required |
| Credentials | Separate local key restricted to the Terra alias |

All pre-existing LiteLLM routes, OpenCode providers and the default OpenCode model were preserved. No account budget was changed. Direct smoke requests used a 2,048-token output limit; this is not a study budget. Temperature was not explicitly set. Context/output metadata is 1,050,000/128,000 tokens; those limits were not stress-tested.

The OpenAI-hosted endpoint initially returned HTTP 404 because the account requires zero data retention. Azure served the **same model** under that policy. No privacy setting was relaxed. This is an explicit provider choice, not an automatic fallback.

## Checks

| Check | Result |
|---|---|
| Exact plain-text reply | Pass |
| Streaming reply and final usage | Pass |
| Forced tool call and arguments | Pass |
| Tool-result round trip | Pass |
| Strict JSON schema response | Pass |
| OpenCode shell write, shell read, exact final answer | Pass |
| File independently verified in disposable workspace | Pass |
| Provider cost/token reconciliation | Pass for two OpenCode calls cross-checked with OpenRouter |

The final OpenCode check took **5.765 seconds**, exited 0 and made two shell calls across three model steps. Its reported cost was **$0.00618925**. This is transport latency with tools and startup included, not coding-task runtime or exclusive inference time.

Known successful readiness calls, including setup retries and the direct Azure probe, reported **$0.01907275** in total. LiteLLM recorded zero cost for the rejected OpenAI-provider request; a provider invoice for that failed request was not independently verified. The OpenCode configuration failure made no model call. Coordinator usage is not included in these smoke-call totals.

## Measurement details

The three final OpenCode steps reconcile to LiteLLM's 12,674 prompt tokens and 87 completion tokens. In these observed events, OpenCode's `input` excludes cache reads and cache writes; adding those partitions reconstructs provider prompt tokens. OpenCode's `output` excludes its separately reported reasoning tokens; adding reasoning reconstructs provider completion tokens. The provider reports reasoning as a subset of completion tokens. `cache_creation_tokens` duplicates `cache_write_tokens` here and must not be added again. Native step events are incremental across the three requests.

Costs from OpenCode, LiteLLM and OpenRouter are cross-checks of the same requests, not additive charges. Cache-write billing was observed. Preserve these fields separately in the study collector and requalify the mapping after harness upgrades. Two provider generation records confirmed Azure and the dated model revision; the gateway response uses the local alias.

## Setup failures and repairs

1. A proposed YAML append failed parsing before it was written. The corrected append passed validation. Service restarts were recorded; readiness waited for startup.
2. The first provider selection was incompatible with account ZDR policy. A direct Azure probe passed, then the new route was explicitly pinned to Azure and restarted.
3. The initial OpenCode provider used a boolean reasoning capability. OpenCode v2 requires an object (`{"supported": true}`); it skipped the malformed provider and returned “model unavailable.” The corrected provider passed the published schema and appeared in the native model list. Existing unrelated legacy MCP settings do not pass the current full schema; they were preserved.
4. The first successful OpenCode transport run inherited a stale `PWD`, so its shell ran in the parent workspace and loaded global MCP configuration. It used only shell tools, but this was not an isolated pass. Its probe artifact and logs were preserved privately. The launcher then aligned `PWD` with its subprocess working directory. A fresh session used the disposable workspace's policies blocking unrelated providers, MCP, skills, plugins, web search and delegation. Its output file was independently checked there.

These are harness qualification repairs, not hidden rescues of a scored result. Raw events, stderr, failed-attempt records and credential-bearing configuration remain local and private. The [sanitized JSON evidence](terra-openrouter-20261107.json) includes timestamps, prompt hashes, usage and hashes of raw artifacts.

## Study implications and limits

Terra through the same OpenCode/LiteLLM/OpenRouter stack is now a feasible candidate for a revised comparison with GLM. Adopting it requires an explicit registration revision and a common harness freeze. This check does not establish equivalence to Codex, long-run reliability, supervisor/worker orchestration, context compaction, parallel tool behavior, or performance on the proposed benchmark. The configured high reasoning setting and observed reasoning usage are not a measurement of internal reasoning effort.

No benchmark application, reference solution or acceptance check was constructed with Terra during this readiness work. No scored study run was launched.

Provider/configuration references: [OpenRouter Terra](https://openrouter.ai/openai/gpt-6.1-terra), [provider routing](https://openrouter.ai/docs/guides/routing/provider-selection), [ZDR policy](https://openrouter.ai/docs/guides/features/zdr), [LiteLLM OpenRouter adapter](https://docs.litellm.ai/docs/providers/openrouter), [OpenCode provider configuration](https://opencode.ai/docs/providers/), [OpenCode schema](https://opencode.ai/config.json).
