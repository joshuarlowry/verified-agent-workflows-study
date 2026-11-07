# Gemma and GLM ZDR provider probes

On 2026-11-07 UTC, direct OpenRouter probes required `zdr: true`, an exact provider tag, `allow_fallbacks: false` and parameter support. Account privacy settings were preserved. These are small transport probes, not calibration or complete OpenCode/LiteLLM qualification. No existing gateway routes were changed.

| Requested model | Pinned provider tag | Catalog quantization | Plain reply | Tool selection |
|---|---|---|---|---|
| `google/gemma-4-31b-it` | `coreweave/fp4` | FP4 | Pass | Forced named tool: pass |
| `z-ai/glm-5.3-flash` | `relace/fp4` | FP4 | Pass | Forced named tool: HTTP 404; automatic selection: pass |

OpenRouter generation records confirmed CoreWeave serving `google/gemma-4-31b-it-20260402` and Relace serving `z-ai/glm-5.3-flash-20260826`. The automatic GLM tool probe's generation lookup was unavailable when checked; its successful completion identified Relace and the requested alias. Quantization is catalog-reported, not independently audited; two FP4 labels do not establish equivalent serving methods. Terra's separate readiness result used Azure, whose quantization is not disclosed here.

**Important accounting gap:** GLM's plain response reported 89 completion tokens and 104 reasoning tokens; its generation record repeated those native counters. Therefore reasoning cannot simply be assumed to be a subset of completion on this route. Do not add or subtract these fields until the actual billable/native mapping is established. Its provider-reported cost remains recorded separately. A provider revision, if necessary, requires a recorded choice and fresh qualification.

The failed forced-tool request is retained; the automatic-tool request is a separately recorded capability check, not an identical transport retry. Qualify the tool mode actually used by OpenCode, streaming, tool-result continuation, Context calls and native usage before calibration. No privacy relaxation or model substitution is authorized by these observations.

[Sanitized request results](gemma-glm-zdr-20261107.json) retain prompt hashes, timestamps, elapsed time, usage and provider cross-checks. Raw payloads remain private. Endpoints: [Gemma catalog](https://openrouter.ai/api/v1/models/google/gemma-4-31b-it/endpoints), [GLM catalog](https://openrouter.ai/api/v1/models/z-ai/glm-5.3-flash/endpoints), [OpenRouter ZDR](https://openrouter.ai/docs/guides/features/zdr). Live availability must be rechecked before freezing routes.
