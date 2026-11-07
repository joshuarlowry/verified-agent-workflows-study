"""Opt-in, source-guarded LiteLLM 1.103.3 SSE sentinel repair.

Enable only in the study gateway process, never global site-packages.
"""
import hashlib
import json
import linecache
import inspect
import os
import textwrap

EXPECTED_SOURCE_SHA256 = "dd9f0696b60749d6cd6216eb5b3739e579e792b18fdb24b1b5908d7f02b58ef5"

def apply():
    from importlib.metadata import version
    import litellm.llms.base_llm.base_model_iterator as module
    from pathlib import Path
    if version('litellm') != '1.103.3':
        raise RuntimeError('Unqualified LiteLLM version')
    if hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest() != EXPECTED_SOURCE_SHA256:
        raise RuntimeError('Unqualified upstream source')
    if getattr(module, '_study_done_fix_applied', False):
        return
    original = module.BaseModelResponseIterator._handle_string_chunk
    source = textwrap.dedent(inspect.getsource(original))
    old = 'if "[DONE]" in str_line:'
    new = 'if (litellm.CustomStreamWrapper._strip_sse_data_from_chunk(str_line) or "").strip() == "[DONE]":'
    if source.count(old) != 1:
        raise RuntimeError('Upstream method does not match reviewed patch')
    namespace = {}
    repaired_source = source.replace(old, new)
    filename = '<study-litellm-sse-method>'
    linecache.cache[filename] = (len(repaired_source), None, repaired_source.splitlines(keepends=True), filename)
    exec(compile(repaired_source, filename, 'exec'), module.__dict__, namespace)
    module._study_original_handle_string_chunk = original
    module.BaseModelResponseIterator._handle_string_chunk = namespace['_handle_string_chunk']
    module._study_done_fix_applied = True

def emit(event, **fields):
    os.write(2, (json.dumps({'event': event, **fields})+'\n').encode())

mode = os.environ.get('STUDY_LITELLM_DONE_FIX')
if mode == '1':
    try:
        apply()
        emit('study_litellm_overlay_active', upstream_source_sha256=EXPECTED_SOURCE_SHA256)
    except Exception as error:
        allowed = {'Unqualified LiteLLM version', 'Unqualified upstream source', 'Upstream method does not match reviewed patch'}
        reason = str(error) if str(error) in allowed else type(error).__name__
        emit('study_litellm_overlay_refused', reason=reason)
        os._exit(78)
elif mode:
    emit('study_litellm_overlay_refused', reason='Unrecognized activation mode')
    os._exit(78)
else:
    emit('study_litellm_overlay_disabled')
