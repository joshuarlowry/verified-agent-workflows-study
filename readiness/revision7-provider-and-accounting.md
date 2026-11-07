# Higher-precision Gemma and GLM adapter/accounting checks

These are disposable readiness probes on 2026-11-07 UTC. The canonical candidate selection is in [registration.json](../registration.json); historical provider probes remain preserved. No scored runs or application changes occurred. Existing system LiteLLM routes were not modified.

## Gemma precision

The exact `google/gemma-4-31b-it` model passed a plain reply and automatic tool-call probe pinned to `crusoe/bf16`, with ZDR and parameter support required and provider fallback disabled. The catalog reports BF16; this is not an independent precision audit. The plain call's generation record confirmed Crusoe and `google/gemma-4-31b-it-20260402`. The immediate tool-call generation lookup was unavailable; its response identified Crusoe and the requested alias.

Therefore ZDR does **not** require the previously tested FP4 route. Select Crusoe BF16 as the candidate for every direct/supervised Gemma role, pending full study qualification. No FP4-scored results exist to mix with it. Terra precision remains undisclosed, so residual provider/precision differences remain visible. If this candidate becomes unavailable, stop and register/requalify an explicit alternative; do not silently fall back to FP4. Endpoint catalog: [Gemma providers](https://openrouter.ai/api/v1/models/google/gemma-4-31b-it/endpoints).

## GLM billing reconciliation

The earlier Relace FP4 plain call reported 19 prompt, 89 completion and 104 reasoning tokens. Using the endpoint rate card of $0.0284/M input and $0.0923/M output:

| Billing interpretation | Computed USD |
|---|---:|
| Prompt + completion | 0.0000087543 |
| Prompt + completion + reasoning | 0.0000183535 |
| Provider reported | 0.0000087543 |

Completion-only reproduces the reported bill exactly. The rate card was retrieved again for this check; the exact arithmetic match supports this observed route's billing mapping, not an assumed universal token relationship. Preserve reasoning as a diagnostic counter and do not add it to billed output. [Relace endpoint metadata](https://openrouter.ai/api/v1/models/z-ai/glm-5.3-flash/endpoints).

## Full transport adapter probe

A private, temporary LiteLLM 1.103.3 proxy pinned the exact GLM model to `relace/fp4`, ZDR required, no fallback and no retries. OpenCode 2.2.5 used its OpenAI-compatible adapter with a separate scoped temporary credential. A local pass-through observer captured request tool-selection metadata and raw final SSE usage. All other providers, MCP, skills, web and delegation were denied for this transport test. This is not the study's completed Context/broker qualification.

Two independently recorded successful probes each wrote a fixed marker through shell, read it through shell, returned the exact marker and exited 0. Their durations were 6.935 and 8.483 seconds including startup/tools/waiting. The instrumented probe made three streamed model requests; each **omitted `tool_choice`**, leaving normal automatic selection. Both shell calls and tool-result continuation passed. The earlier forced-tool 404 is therefore not a blocker for this observed normal adapter path; it remains a documented unsupported capability.

Every instrumented request's cost exactly matches prompt plus completion tokens under the rate card. Generation records confirm Relace and `z-ai/glm-5.3-flash-20260826`; generation costs are displayed with less decimal precision than response costs.

There is an important native-counter caveat. In the first instrumented request, provider usage is 245 completion and 272 reasoning tokens. OpenCode reports output 0 and reasoning 272. Reconstructing billable output as native output + reasoning would overcount by 27 tokens. Use captured **raw gateway/provider `usage.completion_tokens`** for this route's billing, preserve native counters separately, and require that capture in the study collector. Cached input is a subset of prompt input; native noncached input plus cache partitions reconciles here. The accounting interpretation is resolved for observed calls; changed providers/adapters require revalidation.

The first launch failed before any model request because a UID switch retained root's state location. The corrected launch uses `runuser` and aligned working directory/PWD. Its failure logs and both successful endpoints remain private and hashed. The usage-instrumented run is a separate measurement probe, not a hidden rescue of a study attempt.

[Sanitized evidence](revision7-provider-and-accounting.json) includes raw usage values, recomputations, native steps, controller timing and artifact hashes. Credentials, ports, raw instructions and raw reasoning remain private.
