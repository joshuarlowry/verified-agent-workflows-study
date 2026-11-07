"""Audit source-free/constructor stream fidelity; never grade feature quality."""
from pathlib import Path
import json,hashlib,sys
def parse(path):
 sem={'text':{},'reasoning':{},'tools':{}};ids=set();terminal=False;late=False;finish={};usages=[]
 for line in path.read_bytes().splitlines():
  if not line.startswith(b'data:'):continue
  payload=line.split(b':',1)[1].strip()
  if payload==b'[DONE]':terminal=True;continue
  if not payload:continue
  x=json.loads(payload)
  if not isinstance(x,dict) or x.get('error'):raise ValueError('Invalid/error stream')
  if x.get('id'):ids.add(x['id'])
  if x.get('usage'):usages.append(x['usage'])
  for c in x.get('choices') or []:
   i=str(c.get('index',0));delta=c.get('delta') or {}
   data=bool(delta.get('content') or delta.get('reasoning') or delta.get('reasoning_content') or delta.get('tool_calls'))
   if data and (terminal or i in finish):late=True
   sem['text'][i]=sem['text'].get(i,'')+(delta.get('content') or '')
   reasoning=delta.get('reasoning_content')
   if reasoning is None:reasoning=delta.get('reasoning') or ''
   sem['reasoning'][i]=sem['reasoning'].get(i,'')+reasoning
   for t in delta.get('tool_calls') or []:
    k=i+':'+str(t.get('index',0));v=sem['tools'].setdefault(k,{'name':'','arguments':''});f=t.get('function') or {}
    v['name']+=f.get('name') or '';v['arguments']+=f.get('arguments') or ''
   if c.get('finish_reason') is not None:finish[i]=c['finish_reason']
 return {'semantic':sem,'response_ids':sorted(ids),'terminal_marker':terminal,'late_data':late,'usage':usages}

def index(path):
 return int(path.stem.rsplit('-',1)[1])

RETRYABLE_CODES={429,500,502,503,504}

def failed_body(path):
 """Retain body provenance; a code in a body is not an observed HTTP status."""
 import re
 raw=path.read_bytes();code=None;encoding='unknown_non_json'
 try:
  obj=json.loads(raw);error=obj.get('error',{}) if isinstance(obj,dict) else {}
  code=error.get('code') if isinstance(error,dict) else None;encoding='json_error_body'
 except (ValueError,UnicodeError):
  match=re.fullmatch(rb'error code: ([0-9]{3})\s*',raw)
  if match:code=int(match.group(1));encoding='canonical_plain_error_body'
 if isinstance(code,str) and code.isdigit():code=int(code)
 return {'request':index(path),'provider_error_code':code,'code_provenance':encoding,
         'http_status_independently_captured':False,'capture_sha256':hashlib.sha256(raw).hexdigest(),
         'usage_status':'unavailable; not assumed zero','kind':'failed_http_response_body'}

def explicit_stream_error(path):
 errors=[]
 for line in path.read_bytes().splitlines():
  if not line.startswith(b'data:'):continue
  payload=line.split(b':',1)[1].strip()
  if not payload or payload==b'[DONE]':continue
  obj=json.loads(payload)
  if isinstance(obj,dict) and obj.get('error'):
   error=obj['error'];code=error.get('code') if isinstance(error,dict) else None
   if isinstance(code,str) and code.isdigit():code=int(code)
   errors.append(code)
 if not errors:return None
 return {'request':index(path),'provider_error_code':errors[-1],
         'code_provenance':'explicit_provider_SSE_error','http_status_independently_captured':False,
         'capture_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
         'usage_status':'unavailable; not assumed zero','kind':'failed_provider_stream'}

def classify(run):
 success=[];errors=[]
 for path in sorted(run.glob('provider-response-*.sse'),key=index):
  error=explicit_stream_error(path)
  if error:
   error['gateway_stream_absent'] = not (run/f'gateway-response-{index(path)}.sse').exists()
   errors.append(error)
  else:success.append(path)
 errors.extend(failed_body(path) for path in sorted(run.glob('provider-http-error-*.json'),key=index))
 return success,errors

def usage_by_id(run):
 rows=json.loads((run/'provider-usage.json').read_text());out={}
 for row in rows:
  rid=row['response_id']
  if rid in out:raise ValueError('Duplicate provider usage identity')
  out[rid]=row
 return out

def normalized_usage_matches(normalized,provider):
 # Historical provider-usage.json stores LiteLLM's normalized usage, which
 # drops provider pricing metadata and adds a zero cache_creation counter.
 for key in ['prompt_tokens','completion_tokens','total_tokens','cost']:
  if key not in normalized or key not in provider or normalized[key]!=provider[key]:return False
 for key in ['prompt_tokens_details','completion_tokens_details']:
  a=normalized.get(key,{});b=provider.get(key,{})
  for counter in set(a)|set(b):
   if counter=='cache_creation_tokens' and counter not in b and a.get(counter)==0:continue
   if counter not in a or counter not in b or a[counter]!=b[counter]:return False
 return True

def usage_for(path,lookup):
 parsed=parse(path);ids=parsed['response_ids']
 if len(ids)!=1 or ids[0] not in lookup:raise ValueError('Missing/ambiguous provider usage identity')
 row=lookup[ids[0]]
 if not parsed['usage'] or not normalized_usage_matches(row['usage'],parsed['usage'][-1]):raise ValueError('Provider usage evidence mismatch')
 return row

def compaction_proof(run,j):
 request=run/f'native-request-{j}.json';following=run/f'native-request-{j+1}.json'
 if not following.exists():return None
 a=json.loads(request.read_text());n=json.loads(following.read_text());last=a['messages'][-1]
 if last.get('role')!='user' or not isinstance(last.get('content'),str) or not last['content'].startswith(('You MUST summarize the conversation above into a structured summary','Update the existing checkpoint in the conversation above into one consolidated summary.')):return None
 x=parse(run/f'provider-response-{j}.sse');y=parse(run/f'gateway-response-{j}.sse');text=''.join(y['semantic']['text'].values())
 if not text or y['semantic']['tools'] or x['semantic']!=y['semantic'] or not x['terminal_marker'] or not y['terminal_marker'] or x['late_data'] or y['late_data']:raise ValueError('Invalid compaction stream')
 if not any(m.get('role')=='user' and isinstance(m.get('content'),str) and text in m['content'] and '<conversation-checkpoint>' in m['content'] for m in n['messages']):raise ValueError('Compaction result not consumed verbatim')
 return text

def step_matches(step,row):
 t=step['tokens'];cache=t.get('cache',{});raw=row['usage']
 return t['input']+cache.get('read',0)+cache.get('write',0)==raw['prompt_tokens'] and abs(step['cost']-raw['cost'])<=1e-12

def record_compaction_calls(run,record,steps):
 paths,errors=classify(run)
 if len(paths)<=len(steps):return
 lookup=usage_by_id(run);mapping=[];extras=[];step_index=0
 evidence={'controller.json','events.jsonl','provider-usage.json'}
 for path in paths:
  j=index(path);row=usage_for(path,lookup)
  if compaction_proof(run,j) is not None:
   extras.append({'request':j,'response_id':row['response_id'],'classification':'native_context_compaction',
    'basis':'Captured harness summary consumed verbatim in the following conversation checkpoint; no tools.',
    'usage':row['usage'],'usage_policy':'Include once; no separate operator charge.'})
   evidence.update({f'native-request-{j}.json',f'native-request-{j+1}.json',path.name,f'gateway-response-{j}.sse'})
  elif step_index<len(steps) and step_matches(steps[step_index],row):
   mapping.append({'native_step':step_index+1,'request':j,'response_id':row['response_id']});step_index+=1
  else:raise ValueError('Unsupported native/provider call mapping')
 if step_index!=len(steps) or not extras:raise ValueError('Incomplete native reconciliation')
 report={'kind':'explicit_native_compaction_reconciliation','version':2,'run_id':run.name,'native_steps':len(steps),
  'requests':len(record['requests']),'mapping':mapping,'non_step_calls':extras,
  'failed_requests':[e['request'] for e in errors],
  'evidence_sha256':{name:hashlib.sha256((run/name).read_bytes()).hexdigest() for name in sorted(evidence)},
  'method':'Physical request IDs and stable provider response IDs; usage equality and captured summary-consumption proof. Failed attempts retained separately with unavailable billing.'}
 target=run/'native-call-reconciliation.json'
 with target.open('x') as out:out.write(json.dumps(report,indent=2)+'\n')

def verified_non_step_calls(run,record,steps):
 path=run/'native-call-reconciliation.json'
 if not path.exists():record_compaction_calls(run,record,steps)
 if not path.exists():return 0
 d=json.loads(path.read_text())
 if d.get('kind')!='explicit_native_compaction_reconciliation' or d.get('run_id')!=run.name:raise ValueError('Invalid reconciliation identity')
 for name,digest in d['evidence_sha256'].items():
  if Path(name).name!=name or hashlib.sha256((run/name).read_bytes()).hexdigest()!=digest:raise ValueError('Reconciliation evidence changed')
 lookup=usage_by_id(run);mapped=set();native=set();extras=set()
 for row in d['mapping']:
  i,j=row['native_step'],row['request'];u=usage_for(run/f'provider-response-{j}.sse',lookup)
  if i in native or j in mapped or not 1<=i<=len(steps):raise ValueError('Duplicate/invalid reconciliation mapping')
  if not step_matches(steps[i-1],u) or row['response_id']!=u['response_id']:raise ValueError('Native usage mapping mismatch')
  native.add(i);mapped.add(j)
 if native!=set(range(1,len(steps)+1)):raise ValueError('Unmapped native steps')
 for row in d['non_step_calls']:
  j=row['request'];u=usage_for(run/f'provider-response-{j}.sse',lookup)
  if j in mapped or j in extras or row['classification']!='native_context_compaction' or compaction_proof(run,j) is None:raise ValueError('Unsupported non-step call')
  if row['response_id']!=u['response_id'] or row['usage']!=u['usage']:raise ValueError('Compaction usage mismatch')
  extras.add(j)
 success,errors=classify(run);success_ids={index(p) for p in success};error_ids={e['request'] for e in errors}
 if mapped|extras!=success_ids or not success_ids.isdisjoint(error_ids) or success_ids|error_ids!=set(range(1,len(record['requests'])+1)):raise ValueError('Unreconciled requests')
 return len(extras)

def main():
 run=Path(sys.argv[1]);record=json.loads((run/'controller.json').read_text())
 provider,errors=classify(run);gateway=sorted(run.glob('gateway-response-*.sse'),key=index)
 events=[]
 for line in (run/'events.jsonl').read_text().splitlines():
  try:events.append(json.loads(line))
  except ValueError:pass
 steps=[e['part'] for e in events if e.get('type')=='step_finish']
 non_step_calls=verified_non_step_calls(run,record,steps)
 success_ids={index(p) for p in provider};gateway_ids={index(p) for p in gateway};error_ids={row['request'] for row in errors}
 expected_ids=set(range(1,len(record.get('requests',[]))+1))
 checks={'process_exit_zero':record.get('exit_code')==0,'budget_not_exhausted':not record.get('api_budget_exhausted',False),
  'startup_identity_recorded':(run/'startup-verified.json').exists(),
  'all_stream_calls_paired':bool(provider) and success_ids==gateway_ids and len(provider)==len(steps)+non_step_calls,
  'all_requests_accounted':success_ids.isdisjoint(error_ids) and success_ids|error_ids==expected_ids and len(error_ids)==len(errors) and {index(p) for p in run.glob('provider-request-*.json')}==expected_ids and {index(p) for p in run.glob('native-request-*.json')}==expected_ids,
  'recognized_failed_response_bodies':all(row['provider_error_code'] in RETRYABLE_CODES for row in errors),
  'failed_stream_not_delivered_as_success':all(row.get('gateway_stream_absent',True) for row in errors),
  'native_final_stop':bool(steps) and steps[-1].get('reason')=='stop'}
 pairs=[]
 for a in provider:
  b=run/f'gateway-response-{index(a)}.sse'
  if not b.exists():continue
  x,y=parse(a),parse(b)
  match=x['semantic']==y['semantic'] and x['response_ids']==y['response_ids'] and x['terminal_marker'] and y['terminal_marker'] and not x['late_data'] and not y['late_data']
  pairs.append({'request':index(a),'response_ids':x['response_ids'],'fidelity_and_terminal_order':match,
   'provider_usage_present':bool(x['usage']),'gateway_usage_present':bool(y['usage']),
   'payload_sha256':hashlib.sha256(json.dumps(x['semantic'],sort_keys=True).encode()).hexdigest()})
 checks['all_streams_preserved']=bool(pairs) and len(pairs)==len(provider) and all(x['fidelity_and_terminal_order'] for x in pairs)
 checks['usage_captured']=bool(pairs) and all(x['provider_usage_present'] and x['gateway_usage_present'] for x in pairs)
 report={'kind':'transport_integrity_not_feature_acceptance','all_passed':all(checks.values()),'checks':checks,
  'calls':len(provider),'requests':len(expected_ids),'provider_stream_files':len(list(run.glob('provider-response-*.sse'))),
  'failed_calls':errors,'failed_http_calls':[e for e in errors if e['kind']=='failed_http_response_body'],
  'failed_stream_calls':[e for e in errors if e['kind']=='failed_provider_stream'],'failed_call_billing_complete':not errors,
  'scope':'Successful generation fidelity, native compaction reconciliation and complete request inventory only. Failed response bodies retained; HTTP status/gateway error wire and failed-call billing unavailable. Not full adapter qualification.',
  'verified_non_step_calls':non_step_calls,'pairs':pairs}
 (run/'stream-integrity.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'all_passed':report['all_passed'],'calls':len(provider),'requests':len(expected_ids),'checks':checks}))
 raise SystemExit(0 if report['all_passed'] else 1)
if __name__=='__main__':main()
