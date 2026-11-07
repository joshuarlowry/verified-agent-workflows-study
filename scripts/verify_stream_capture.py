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
def main():
 run=Path(sys.argv[1]);record=json.loads((run/'controller.json').read_text())
 provider=sorted(run.glob('provider-response-*.sse'),key=lambda p:int(p.stem.rsplit('-',1)[1]))
 gateway=sorted(run.glob('gateway-response-*.sse'),key=lambda p:int(p.stem.rsplit('-',1)[1]))
 events=[]
 for line in (run/'events.jsonl').read_text().splitlines():
  try:events.append(json.loads(line))
  except ValueError:pass
 steps=[e['part'] for e in events if e.get('type')=='step_finish']
 checks={'process_exit_zero':record.get('exit_code')==0,'budget_not_exhausted':not record.get('api_budget_exhausted',False),'startup_identity_recorded':(run/'startup-verified.json').exists(),'all_calls_paired':bool(provider) and len(provider)==len(gateway)==len(steps)==len(record.get('requests',[])),'native_final_stop':bool(steps) and steps[-1].get('reason')=='stop'}
 pairs=[]
 for a,b in zip(provider,gateway):
  x,y=parse(a),parse(b)
  match=x['semantic']==y['semantic'] and x['response_ids']==y['response_ids'] and x['terminal_marker'] and y['terminal_marker'] and not x['late_data'] and not y['late_data']
  pairs.append({'response_ids':x['response_ids'],'fidelity_and_terminal_order':match,'provider_usage_present':bool(x['usage']),'gateway_usage_present':bool(y['usage']),'payload_sha256':hashlib.sha256(json.dumps(x['semantic'],sort_keys=True).encode()).hexdigest()})
 checks['all_streams_preserved']=bool(pairs) and all(x['fidelity_and_terminal_order'] for x in pairs)
 checks['usage_captured']=bool(pairs) and all(x['provider_usage_present'] and x['gateway_usage_present'] for x in pairs)
 report={'kind':'transport_integrity_not_feature_acceptance','all_passed':all(checks.values()),'checks':checks,'calls':len(provider),'pairs':pairs}
 (run/'stream-integrity.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'all_passed':report['all_passed'],'calls':len(provider),'checks':checks}))
 raise SystemExit(0 if report['all_passed'] else 1)
if __name__=='__main__':main()
