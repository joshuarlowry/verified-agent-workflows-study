"""Regression controls through real LiteLLM sync/async stream wrappers."""
import asyncio,datetime,importlib.util,json
from pathlib import Path
spec=importlib.util.spec_from_file_location('study_overlay',Path(__file__).with_name('sitecustomize.py'));overlay=importlib.util.module_from_spec(spec);spec.loader.exec_module(overlay);overlay.apply()
import litellm
litellm.suppress_debug_info=True
from litellm.litellm_core_utils.streaming_handler import CustomStreamWrapper
from litellm.litellm_core_utils.litellm_logging import Logging
from litellm.llms.openrouter.chat.transformation import OpenRouterChatCompletionStreamingHandler
def frame(content=None,finish=None):
 return 'data: '+json.dumps({'id':'synthetic-full-wrapper','created':1,'model':'openai/gpt-6.1-terra','choices':[{'index':0,'delta':{'content':content},'finish_reason':finish}]})
def log():
 return Logging(model='openai/gpt-6.1-terra',messages=[],stream=True,call_type='completion',start_time=datetime.datetime.now(),litellm_call_id='synthetic-wrapper',function_id='synthetic-wrapper')
def run_sync(rows):
 iterator=OpenRouterChatCompletionStreamingHandler(iter(rows),sync_stream=True)
 return list(CustomStreamWrapper(iterator,model='openai/gpt-6.1-terra',logging_obj=log(),custom_llm_provider='openrouter'))
class AsyncRows:
 def __init__(self,rows):self.rows=iter(rows)
 def __aiter__(self):return self
 async def __anext__(self):
  try:return next(self.rows)
  except StopIteration:raise StopAsyncIteration
async def run_async(rows):
 iterator=OpenRouterChatCompletionStreamingHandler(AsyncRows(rows),sync_stream=False)
 wrapper=CustomStreamWrapper(iterator,model='openai/gpt-6.1-terra',logging_obj=log(),custom_llm_provider='openrouter')
 return [chunk async for chunk in wrapper]
checks=[]
valid=[b': data: [DONE]',frame('literal [DONE] remains data').encode(),frame(None,'stop').encode(),b'data: [DONE]']
for mode,runner in [('sync',run_sync),('async',lambda r:asyncio.run(run_async(r)))]:
 out=runner(valid)
 text=''.join((c.choices[0].delta.content or '') for c in out if c.choices)
 assert text=='literal [DONE] remains data',(mode,text)
 checks.append(mode+'_valid_literal_and_byte_comment')
 for name,rows in [
  ('suffixed_invalid_marker',[frame('partial'), 'data: [DONE] trailing']),
  ('missing_terminal_marker',[frame('partial')]),
  ('quoted_invalid_marker',[frame('partial'),'data: "[DONE]"']),
  ('data_after_finish',[frame('partial','stop'),frame('late'),'data: [DONE]']),
  ('data_after_marker',[frame('partial'),'data: [DONE]',frame('late')])]:
  try:runner(rows)
  except Exception:checks.append(mode+'_'+name+'_rejected')
  else:raise AssertionError((mode,name,'invalid stream completed'))
print(json.dumps({'kind':'mechanical_no_model_calls','all_passed':True,'checks':checks},indent=2))
