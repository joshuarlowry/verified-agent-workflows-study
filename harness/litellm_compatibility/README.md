# Study-only OpenRouter streaming repair

The installed LiteLLM 1.103.3 parser treats any occurrence of the literal terminal marker inside a JSON event as stream completion. A paired same-generation capture proves that it drops a tool-argument fragment and injects premature stop; OpenRouter's upstream event is valid. Old successful constructor returns cannot rule out silent loss.

The current process-local overlay targets only OpenRouterChatCompletionStreamingHandler. It:

- Recognizes the standalone terminal payload, preserving literals inside content, tool arguments and reasoning.
- Preserves SSE field boundaries for bytes and strings; comments never become terminal markers.
- Rejects malformed JSON/non-object payloads, model data after a finish reason, and data after the terminal marker.
- Raises on EOF without the terminal marker, preventing LiteLLM's full wrapper from synthesizing successful completion of a truncated stream.
- Checks the exact package version and hashes of the upstream base iterator, OpenRouter handler and wrapper source. Installed files and other provider iterators are unchanged.

This is a strict contract for the registered OpenRouter ChatCompletions path, not a general-purpose SSE parser. The [official OpenRouter example](https://github.com/OpenRouterTeam/docs/blob/ee0e76998ffd6ec993fb711924fc805f13c479ec/api_reference/streaming.mdx) compares the raw data payload with the terminal marker before parsing JSON. A quoted JSON string or suffixed marker is not accepted as successful termination. A live provider that cannot meet the contract blocks qualification; it is not counted as an agent-quality failure.

## Mandatory gateway entry point

Clean jobs invoke launch_gateway.py in the pinned virtual environment, with the frozen patch hash, overlay PYTHONPATH and activation value 1. The launcher requires the module to have loaded at interpreter startup, checks its exact file and hash, and verifies the actual three active method bindings. A historical applied flag is insufficient. Any mismatch refuses startup before the CLI/model call.

It emits study_gateway_verified with hashes. The controller must observe that record before dispatch. Direct legacy CLI launches are excluded. The gateway process uses this startup module instead of the host apport startup hook; record that difference. The shared system gateway remains unchanged.

## Qualification

Run check_sentinel.py, check_full_wrapper.py and check_gateway_startup.py using the pinned environment. The original substring defect is a negative control. Valid bytes/literals must pass; malformed and truncated streams must fail through the actual sync and async LiteLLM wrappers. Startup tests restore a defective method while keeping the legacy flag and require refusal.

Captured-stream replay, fresh native tool/file tests for all three registered models, raw provider/gateway/native capture, and different-model review are required. Use the same final frozen overlay for every role. The earlier repair candidates and review findings remain engineering history; none is a clean benchmark fixture or scored result. No candidate here enables calibration or scored dispatch.
