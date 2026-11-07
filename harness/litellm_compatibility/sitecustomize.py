"""Opt-in, source-guarded LiteLLM 1.103.3 SSE sentinel repair.

Enable only in the study gateway process, never global site-packages.
"""
import hashlib
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
    exec(compile(source.replace(old, new), __file__ + ':guarded-upstream-method', 'exec'), module.__dict__, namespace)
    module._study_original_handle_string_chunk = original
    module.BaseModelResponseIterator._handle_string_chunk = namespace['_handle_string_chunk']
    module._study_done_fix_applied = True

if os.environ.get('STUDY_LITELLM_DONE_FIX') == '1':
    try:
        apply()
    except Exception:
        # Python otherwise ignores sitecustomize import errors and continues.
        os.write(2, b'Study LiteLLM compatibility verification failed; refusing startup\n')
        os._exit(78)
