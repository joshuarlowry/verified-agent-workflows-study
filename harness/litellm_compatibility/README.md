# Study-only LiteLLM SSE repair candidate

LiteLLM 1.103.3's `BaseModelResponseIterator._handle_string_chunk` checks whether `[DONE]` occurs anywhere in a raw event. A normal JSON content/tool/reasoning fragment containing that literal is replaced by a synthetic `stop` fragment. Subsequent tool arguments then make OpenCode reject the response. The affected fragment is also lost; suppressing the downstream exception would not recover correct content.

The paired capture records the **same generation** before and after LiteLLM: the provider stream has no late content, while the gateway injects `stop` at the fragment containing the literal. Raw captures and payloads remain private. See [diagnostic evidence](../../setup/transport-diagnosis.json).

`sitecustomize.py` changes only the marker predicate to an equality check on the stripped SSE payload. It verifies the exact installed package version and upstream source hash, then compiles that one changed method in the original module namespace. It does not rewrite installed source, discard fragments, reconstruct tool arguments or choose a different model/provider. A failed compatibility check terminates startup with exit 78; Python's normally ignored `sitecustomize` error is insufficient.

Enable only for the study gateway process, before launching it:

```sh
PYTHONPATH="$PWD/harness/litellm_compatibility" \
STUDY_LITELLM_DONE_FIX=1 \
/opt/hermes/litellm-1.103.3/venv/bin/litellm --config PRIVATE_CONFIG --host 127.0.0.1 --port PRIVATE_PORT
```

The process uses the study startup module instead of the host's default apport startup hook. This difference belongs in the frozen gateway manifest. Model parameters and provider pins are unchanged. The shared system gateway is untouched. The same qualified overlay must be used for every scored model and role; mixed patched/unpatched collection is prohibited.

Run the actual sync/async iterator regressions without the opt-in flag:

```sh
/opt/hermes/litellm-1.103.3/venv/bin/python harness/litellm_compatibility/check_sentinel.py
```

The negative control reproduces the original defect. Checks cover content, tool arguments, reasoning, real marker variants, sync/async continuation, budget errors and usage. Captured-stream replay, native tool/file round trips and different-model cross-review are also required. A passing unit check is not full role, worker-broker or acceptance qualification. This candidate cannot itself enable registered dispatch.
