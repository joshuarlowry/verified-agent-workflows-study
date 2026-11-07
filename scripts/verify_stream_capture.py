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
def verified_non_step_calls(run,record,steps):
 path=run/'native-call-reconciliation.json'
 if not path.exists():return 0
 d=json.loads(path.read_text())
 if d.get('kind')!='explicit_native_compaction_reconciliation' or d.get('run_id')!=run.name:raise ValueError('Invalid reconciliation identity')
 for name,digest in d['evidence_sha256'].items():
  if Path(name).name!=name or hashlib.sha256((run/name).read_bytes()).hexdigest()!=digest:raise ValueError('Reconciliation evidence changed')
 usage=json.loads((run/'provider-usage.json').read_text());mapped=set();native=set()
 for row in d['mapping']:
  i,j=row['native_step'],row['request'];t=steps[i-1]['tokens'];u=usage[j-1]
  if i in native or j in mapped:raise ValueError('Duplicate reconciliation mapping')
  if t['input']+t['cache']['read']+t['cache']['write']!=u['usage']['prompt_tokens'] or abs(steps[i-1]['cost']-u['usage']['cost'])>1e-12 or row['response_id']!=u['response_id']:raise ValueError('Native usage mapping mismatch')
  native.add(i);mapped.add(j)
 if native!=set(range(1,len(steps)+1)):raise ValueError('Unmapped native steps')
 extras=set()
 for row in d['non_step_calls']:
  j=row['request']
  if j in mapped or j in extras or row['classification']!='native_context_compaction':raise ValueError('Unsupported non-step call')
  a=json.loads((run/f'native-request-{j}.json').read_text());n=json.loads((run/f'native-request-{j+1}.json').read_text());y=parse(run/f'gateway-response-{j}.sse');text=''.join(y['semantic']['text'].values())
  if not a['messages'][-1]['content'].startswith('You MUST summarize the conversation above into a structured summary') or not text or y['semantic']['tools']:raise ValueError('Unsupported compaction request')
  if not any(isinstance(m.get('content'),str) and text in m['content'] and '<conversation-checkpoint>' in m['content'] for m in n['messages']):raise ValueError('Compaction result not consumed verbatim')
  if row['response_id']!=usage[j-1]['response_id'] or row['usage']!=usage[j-1]['usage']:raise ValueError('Compaction usage mismatch')
  extras.add(j)
 if mapped|extras!=set(range(1,len(record['requests'])+1)):raise ValueError('Unreconciled requests')
 return len(extras)
def main():
 run=Path(sys.argv[1]);record=json.loads((run/'controller.json').read_text())
 provider=sorted(run.glob('provider-response-*.sse'),key=lambda p:int(p.stem.rsplit('-',1)[1]))
 gateway=sorted(run.glob('gateway-response-*.sse'),key=lambda p:int(p.stem.rsplit('-',1)[1]))
 events=[]
 for line in (run/'events.jsonl').read_text().splitlines():
  try:events.append(json.loads(line))
  except ValueError:pass
 steps=[e['part'] for e in events if e.get('type')=='step_finish']
 non_step_calls=verified_non_step_calls(run,record,steps)
 checks={'process_exit_zero':record.get('exit_code')==0,'budget_not_exhausted':not record.get('api_budget_exhausted',False),'startup_identity_recorded':(run/'startup-verified.json').exists(),'all_calls_paired':bool(provider) and len(provider)==len(gateway)==len(steps)+non_step_calls==len(record.get('requests',[])),'native_final_stop':bool(steps) and steps[-1].get('reason')=='stop'}
 pairs=[]
 for a,b in zip(provider,gateway):
  x,y=parse(a),parse(b)
  match=x['semantic']==y['semantic'] and x['response_ids']==y['response_ids'] and x['terminal_marker'] and y['terminal_marker'] and not x['late_data'] and not y['late_data']
  pairs.append({'response_ids':x['response_ids'],'fidelity_and_terminal_order':match,'provider_usage_present':bool(x['usage']),'gateway_usage_present':bool(y['usage']),'payload_sha256':hashlib.sha256(json.dumps(x['semantic'],sort_keys=True).encode()).hexdigest()})
 checks['all_streams_preserved']=bool(pairs) and all(x['fidelity_and_terminal_order'] for x in pairs)
 checks['usage_captured']=bool(pairs) and all(x['provider_usage_present'] and x['gateway_usage_present'] for x in pairs)
 report={'kind':'transport_integrity_not_feature_acceptance','all_passed':all(checks.values()),'checks':checks,'calls':len(provider),'verified_non_step_calls':non_step_calls,'pairs':pairs}
 (run/'stream-integrity.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'all_passed':report['all_passed'],'calls':len(provider),'checks':checks}))
 raise SystemExit(0 if report['all_passed'] else 1)
if __name__=='__main__':main()
