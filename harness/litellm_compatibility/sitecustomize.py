"""Opt-in, source-guarded strict SSE repair for study OpenRouter gateways.

Installed package files and other provider iterators are never rewritten.
"""
import hashlib
import inspect
import json
import linecache
import os
import re
import textwrap
from pathlib import Path

UPSTREAM_GUARDS = {'llms/base_llm/base_model_iterator.py': 'dd9f0696b60749d6cd6216eb5b3739e579e792b18fdb24b1b5908d7f02b58ef5', 'llms/openrouter/chat/transformation.py': '8a7936d6dcca86bcddda9ac18d7cb6aaf76d98fc1bb73652f6abef659fa926f7', 'litellm_core_utils/streaming_handler.py': 'a4e630f212320b8c5871f6f6a8219f96459cde4cd3c03fed8582f813fd71eb29'}
EXPECTED_SOURCE_SHA256 = UPSTREAM_GUARDS['llms/base_llm/base_model_iterator.py']
_PATCHED = {}
_TARGET = None

def _empty(finished=False):
    from litellm.types.utils import GenericStreamingChunk
    return GenericStreamingChunk(text="",is_finished=finished,finish_reason="stop" if finished else "",usage=None,index=0,tool_use=None)

def _strict_openrouter_chunk(self, str_line):
    if isinstance(str_line,bytes):
        str_line=str_line.decode('utf-8')
    if not isinstance(str_line,str):
        raise ValueError('Expected an OpenRouter SSE text line')
    line=str_line.strip()
    # These are SSE metadata/comments, never model data or terminal markers.
    if not line or line.startswith(':') or line.startswith(('event:','id:','retry:')):
        return _empty()
    import litellm
    payload=(litellm.CustomStreamWrapper._strip_sse_data_from_chunk(str_line) or '').strip()
    if getattr(self,'_study_terminal_seen',False):
        raise ValueError('OpenRouter data after terminal marker')
    if payload=='[DONE]':
        self._study_terminal_seen=True
        return _empty(True)
    try:
        chunk=json.loads(payload)
    except json.JSONDecodeError as error:
        raise ValueError('Malformed OpenRouter streaming JSON') from error
    if not isinstance(chunk,dict):
        raise ValueError('Expected OpenRouter streaming object')
    finished=getattr(self,'_study_finished_choices',{})
    for choice in chunk.get('choices') or []:
        index=choice.get('index',0)
        delta=choice.get('delta') or {}
        has_data=any(delta.get(key) for key in ('content','tool_calls','reasoning','reasoning_content','reasoning_details'))
        if index in finished and has_data:
            raise ValueError('OpenRouter model data after finish reason')
        reason=choice.get('finish_reason')
        if reason is not None:
            if index in finished and finished[index]!=reason:
                raise ValueError('Conflicting OpenRouter finish reasons')
            finished[index]=reason
    self._study_finished_choices=finished
    return self.chunk_parser(chunk=chunk)

def _iterator_method(base_module,name):
    source=textwrap.dedent(inspect.getsource(getattr(base_module.BaseModelResponseIterator,name)))
    # Keep bytes decoding but preserve the actual SSE field boundary.
    pattern=r'(?m)^([ ]*)index = str_line.find\("data:"\)\n\1if index != -1:\n\1    str_line = str_line\[index:\]\n'
    source,count=re.subn(pattern,'',source)
    if count!=1:
        raise RuntimeError('Unqualified byte preprocessing')
    exception='StopIteration' if name=='__next__' else 'StopAsyncIteration'
    pattern=r'(?m)^([ ]*)except '+exception+r':\n\1    raise '+exception+r'\n'
    def guard(match):
        indent=match.group(1)
        return (indent+'except '+exception+':\n'+indent+'    if not getattr(self,"_study_terminal_seen",False):\n'+indent+'        raise ValueError("Unterminated OpenRouter SSE stream")\n'+indent+'    raise '+exception+'\n')
    source,count=re.subn(pattern,guard,source)
    if count not in (1,2):
        raise RuntimeError('Unqualified iterator EOF handling')
    filename='<study-openrouter-'+name+'>'
    linecache.cache[filename]=(len(source),None,source.splitlines(keepends=True),filename)
    namespace={}
    exec(compile(source,filename,'exec'),base_module.__dict__,namespace)
    return namespace[name]

def verify_active():
    return _TARGET is not None and len(_PATCHED)==3 and all(getattr(_TARGET,name,None) is method for name,method in _PATCHED.items())

def apply():
    global _TARGET,_PATCHED
    from importlib.metadata import version
    import litellm
    import litellm.llms.base_llm.base_model_iterator as base
    from litellm.llms.openrouter.chat.transformation import OpenRouterChatCompletionStreamingHandler
    if version('litellm')!='1.103.3':
        raise RuntimeError('Unqualified LiteLLM version')
    package=Path(litellm.__file__).parent
    if any(hashlib.sha256((package/name).read_bytes()).hexdigest()!=sha for name,sha in UPSTREAM_GUARDS.items()):
        raise RuntimeError('Unqualified upstream source')
    if _PATCHED:
        if not verify_active():
            raise RuntimeError('Active OpenRouter iterator repair changed')
        return
    methods={'_handle_string_chunk':_strict_openrouter_chunk,'__next__':_iterator_method(base,'__next__'),'__anext__':_iterator_method(base,'__anext__')}
    _TARGET=OpenRouterChatCompletionStreamingHandler
    for name,method in methods.items():
        setattr(_TARGET,name,method)
    _PATCHED=methods
    # Legacy diagnostic marker only; the launcher verifies actual methods.
    base._study_done_fix_applied=True

def emit(event,**fields):
    os.write(2,(json.dumps({'event':event,**fields})+'\n').encode())

mode=os.environ.get('STUDY_LITELLM_DONE_FIX')
if mode=='1':
    try:
        apply()
        emit('study_litellm_overlay_active',upstream_source_sha256=EXPECTED_SOURCE_SHA256,scope='OpenRouter strict SSE')
    except Exception as error:
        allowed={'Unqualified LiteLLM version','Unqualified upstream source','Unqualified byte preprocessing','Unqualified iterator EOF handling','Active OpenRouter iterator repair changed'}
        emit('study_litellm_overlay_refused',reason=str(error) if str(error) in allowed else type(error).__name__)
        os._exit(78)
elif mode:
    emit('study_litellm_overlay_refused',reason='Unrecognized activation mode')
    os._exit(78)
else:
    emit('study_litellm_overlay_disabled')
