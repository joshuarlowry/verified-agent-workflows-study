"""Attribute captured provider error bodies by fixed run and role; no grading or inference."""
import argparse
from collections import Counter
import datetime
import hashlib
import json
from pathlib import Path


def packets(raw):
    try:
        value=json.loads(raw)
        return [value] if isinstance(value,dict) else []
    except ValueError:
        found=[]
        for line in raw.splitlines():
            if line.startswith('data:'):
                try:
                    value=json.loads(line[5:].strip())
                    if isinstance(value,dict):found.append(value)
                except ValueError:pass
        return found


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--selection',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args()
    if a.output.exists():raise ValueError('Preserve previous attribution receipts')
    selection=json.loads(a.selection.read_text());rows=[]
    for slot in selection['ordinary_calibration_slots']:
        root=Path(slot['endpoint_root']);roles=[]
        for transport in sorted(root.glob('*-transport')):
            calls=[];models=Counter();groups=Counter();unknown=0;success=0;total=0
            for directory in sorted((transport/'provider').iterdir()):
                if not directory.is_dir():continue
                total+=1;request=directory/'request.body';response=directory/'response.body';model=None
                if request.exists():
                    try:model=json.loads(request.read_text()).get('model')
                    except ValueError:pass
                models[str(model)]+=1
                if not response.exists():unknown+=1;continue
                body=response.read_bytes();values=packets(body.decode(errors='replace'));errors=[];seen=set()
                for value in values:
                    error=value.get('error')
                    if not isinstance(error,dict):continue
                    metadata=error.get('metadata') or {};metadata=metadata if isinstance(metadata,dict) else {};key=(str(error.get('code')),metadata.get('provider_name'))
                    if key in seen:continue
                    seen.add(key);groups[key]+=1
                    raw=str(metadata.get('raw',''));message=error.get('message');errors.append({'body_error_code':key[0],'body_identified_provider':key[1],'message':message if message in ['Provider returned error','Upstream idle timeout exceeded'] else 'Message retained privately.','upstream_rate_limit_explicit':'temporarily rate-limited upstream' in raw})
                if errors:calls.append({'capture_call_id':directory.name,'requested_model':model,'response_body_sha256':hashlib.sha256(body).hexdigest(),'errors_deduplicated_within_call':errors})
                elif any(value.get('usage') for value in values):success+=1
                else:unknown+=1
            roles.append({'role':transport.name.removesuffix('-transport'),'captured_provider_calls':total,'requested_models':dict(models),'failed_call_bodies':len(calls),'successful_usage_bodies':success,'unknown_or_unclassified_bodies':unknown,'error_groups':[{'body_error_code':k[0],'body_identified_provider':k[1],'unique_call_count':v} for k,v in sorted(groups.items(),key=lambda x:str(x[0]))],'failed_calls':calls})
            assert total==len(calls)+success+unknown
        rows.append({'run_id':slot['run_id'],'arm':slot['arm'],'repetition':slot['repetition'],'roles':roles})
    report={'kind':'C1_fixed_nominal_run_provider_error_body_attribution_not_regrading','observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'selection_sha256':hashlib.sha256(a.selection.read_bytes()).hexdigest(),'model_calls':0,'rows':rows,'scope':'All ten fixed nominal C1 endpoints; technical extras and preparation calls remain in their separate records. Provider wire captures only; gateway/native views are not added.','limits':['Error codes and provider names here come from captured response bodies; this report does not separately assert HTTP status.','One provider call ID is counted once as failed; repeated identical error packets within it are deduplicated. Different error kinds within one call are diagnostic groups, not additional paid calls.','Unknown/unclassified responses are not zero errors or successful inference. Missing failed-call usage remains unavailable, not free.','A body identifying Crusoe establishes reported upstream-route attribution, not physical serving attestation. Timeouts without provider metadata cannot identify the exact failing component.','Endpoint causes, original source/Beads, native usage, timing and acceptance scores are unchanged. This is descriptive pilot infrastructure evidence, not a model-quality ranking.']}
    a.output.write_text(json.dumps(report,indent=2)+'\n')
    for row in rows:
        for role in row['roles']:
            if role['failed_call_bodies']:print(row['run_id'],role['role'],role['error_groups'])


if __name__=='__main__':main()
