"""Real LiteLLM iterator regressions; no credentials or model calls."""
import asyncio
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import importlib.util
spec=importlib.util.spec_from_file_location("study_litellm_patch",Path(__file__).with_name("sitecustomize.py"))
sitecustomize=importlib.util.module_from_spec(spec)
spec.loader.exec_module(sitecustomize)
from litellm.llms.openrouter.chat.transformation import OpenRouterChatCompletionStreamingHandler

def chunk(delta, finish=None, usage=None):
    x={'id':'synthetic-sentinel','created':1,'model':'openai/gpt-6.1-terra','choices':[{'index':0,'delta':delta,'finish_reason':finish}]}
    if usage is not None:x['usage']=usage
    return 'data: '+json.dumps(x)+'\n'

def parse(line):
    handler=OpenRouterChatCompletionStreamingHandler(iter([]),sync_stream=True)
    return handler._handle_string_chunk(line)

def view(x):
    return x.model_dump() if hasattr(x,'model_dump') else x

# Negative control: demonstrate the actual installed upstream defect.
text='literal [DONE] inside ordinary content'
pre=view(parse(chunk({'content':text})))
assert pre.get('is_finished') is True and pre.get('finish_reason')=='stop',pre
sitecustomize.apply()
checks=[]
for label,delta in [('content',{'content':text}),('tool_arguments',{'tool_calls':[{'index':0,'id':'call1','type':'function','function':{'name':'write','arguments':json.dumps({'content':text})}}]}),('reasoning',{'reasoning':text})]:
    data=view(parse(chunk(delta)))
    c=data['choices'][0]
    assert c['finish_reason'] is None,(label,data)
    if label=='content':assert c['delta']['content']==text
    if label=='tool_arguments':assert json.loads(c['delta']['tool_calls'][0]['function']['arguments'])['content']==text
    if label=='reasoning':assert c['delta']['reasoning_content']==text
    checks.append(label+'_preserved')
for sentinel in ['data: [DONE]','data:[DONE]\n','[DONE]','data:  [DONE]  \n']:
    data=view(parse(sentinel));assert data['is_finished'] is True and data['finish_reason']=='stop',data
checks.append('real_sentinel_variants_end')
stream=[chunk({'content':'first [DONE] literal'}),chunk({'content':' second'}),chunk({},'stop'),'data: [DONE]']
sync=list(OpenRouterChatCompletionStreamingHandler(iter(stream),sync_stream=True))
assert ''.join(x.choices[0].delta.content or '' for x in sync if hasattr(x,'choices'))=='first [DONE] literal second'
checks.append('sync_iteration_continues_after_literal')
class AsyncLines:
    def __aiter__(self):
        async def lines():
            for line in stream:yield line
        return lines()
async def verify():
    out=[]
    async for x in OpenRouterChatCompletionStreamingHandler(AsyncLines(),sync_stream=False):out.append(x)
    assert ''.join(x.choices[0].delta.content or '' for x in out if hasattr(x,'choices'))=='first [DONE] literal second'
asyncio.run(verify());checks.append('async_iteration_continues_after_literal')
# A real provider error must remain an error, including a marker in its text.
try:parse('data: '+json.dumps({'error':{'code':402,'message':'credit limit [DONE] literal'}}))
except Exception as e:
    assert getattr(e,'status_code',None)==402,(type(e).__name__,str(e));checks.append('budget_error_not_swallowed')
else:raise AssertionError('Budget error was swallowed')
usage={'prompt_tokens':3,'completion_tokens':4,'total_tokens':7}
line=json.loads(chunk({})[6:]);line.update(choices=[],usage=usage)
data=view(parse('data: '+json.dumps(line)));assert data['usage']['total_tokens']==7;checks.append('usage_preserved')
print(json.dumps({'kind':'mechanical_no_model_calls','upstream_bug_negative_control':True,'checks':checks,'all_passed':True},indent=2))
