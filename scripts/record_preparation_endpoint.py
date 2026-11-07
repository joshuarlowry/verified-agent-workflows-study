"""Export sanitized metadata from an already-returned private preparation run.

No model dispatch. Generation API lookups only cross-check first/last route;
raw usage/native logs remain private and are hashed. Missing cost stays null.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import urllib.parse
import urllib.request

parser=argparse.ArgumentParser()
parser.add_argument('--run',required=True)
parser.add_argument('--output',required=True)
parser.add_argument('--model',required=True,choices=['google/gemma-4-31b-it','z-ai/glm-5.3-flash','openai/gpt-6.1-terra'])
parser.add_argument('--provider-tag',required=True)
parser.add_argument('--reasoning')
a=parser.parse_args()
root=Path('/home/josh/.local/state/study2-setup').resolve()
d=(root/a.run).resolve()
if d.parent!=root:raise ValueError('Preparation run must be a direct child of private setup root')
c=json.loads((d/'controller.json').read_text())
if 'provider_usage' not in c:raise ValueError('No completed endpoint/usage collection')
events_file=d/'events.jsonl'
events=[json.loads(l) for l in events_file.read_text().splitlines() if l.startswith('{')]
unique={}
for row in c['provider_usage']:
    ident=row.get('response_id')
    if not ident:raise ValueError('Captured usage lacks response identity')
    if ident in unique and unique[ident]!=row:raise ValueError('Conflicting raw usage snapshots require reconciliation')
    unique[ident]=row
rows=list(unique.values())
checks=[]
if rows:
    key=Path('/run/credentials/hermes-litellm.service/OPENROUTER_API_KEY').read_text().strip()
    for row in [rows[0],rows[-1]]:
        request=urllib.request.Request('https://openrouter.ai/api/v1/generation?'+urllib.parse.urlencode({'id':row['response_id']}),headers={'Authorization':'Bearer '+key})
        with urllib.request.urlopen(request,timeout=45) as response:data=json.load(response)['data']
        checks.append({k:data.get(k) for k in ['model','provider_name','total_cost','native_tokens_prompt','native_tokens_completion','native_tokens_reasoning']})
def total(field):
    values=[r['usage'].get(field) for r in rows]
    return sum(values) if values and all(x is not None for x in values) else None
names=sorted({e['part'].get('tool') for e in events if e.get('type')=='tool_use'})
report={'run_id':a.run,'requested_model':a.model,'expected_provider_tag':a.provider_tag,'reasoning_effort_configured':a.reasoning,'generation_crosschecks_first_last':checks,'dispatch_utc':c['dispatch_utc'],'elapsed_seconds':c['elapsed_seconds'],'exit_code':c['exit_code'],'native_steps':len(c['steps']),'provider_usage_calls':len(rows),'native_session_ids':sorted({e['sessionID'] for e in events if e.get('sessionID')}),'reported_model_cost_usd':total('cost'),'raw_usage_prompt_tokens_inclusive_cache':total('prompt_tokens'),'raw_usage_completion_tokens_do_not_add_reasoning':total('completion_tokens'),'prompt_sha256':hashlib.sha256((d/'prompt.txt').read_bytes()).hexdigest(),'raw_events_sha256':hashlib.sha256(events_file.read_bytes()).hexdigest(),'observed_tool_call_counts':{name:sum(e.get('type')=='tool_use' and e['part'].get('tool')==name for e in events) for name in names},'evidence_scope':'preparation only; raw observed usage deduplicated by response id, native counters are cross-checks; first/last generation resolution only, failed uncaptured usage not inferred; no full capture qualification'}
output=Path(a.output).resolve();output.parent.mkdir(exist_ok=True,parents=True)
if output.exists():raise ValueError('Endpoint metadata exists; do not overwrite')
output.write_text(json.dumps(report,indent=2)+'\n')
if os.getuid()==0:os.chown(output,1000,1000);os.chown(output.parent,1000,1000)
print(json.dumps({'run':a.run,'exit_code':c['exit_code'],'captured_calls':len(rows),'output':str(output)}))
