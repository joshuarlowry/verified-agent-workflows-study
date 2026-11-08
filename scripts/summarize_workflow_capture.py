"""Minimal offline pilot accounting: provider billing once, native diagnostics apart.

Reads root-protected role captures only. No model calls, grading, price modeling,
retry, or data repair. Failed/missing/conflicting usage stays explicitly unknown.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
from verify_stream_capture import parse


def rows(path):
    return [json.loads(x) for x in path.read_text().splitlines() if x.strip()]


def summarize(root):
    root=Path(root);result=[];seen={}
    for role in ['complete_agent','supervisor','worker']:
        transport=root/(role+'-transport')
        if not transport.exists():continue
        providers={};gateways={};unknown=[]
        for kind,target in [('provider',providers),('gateway-calls',gateways)]:
            for directory in sorted((transport/kind).glob('*')):
                events=rows(directory/'events.jsonl');headers=[x for x in events if x.get('kind')=='headers'];status=headers[-1].get('status') if headers else None
                body=directory/'response.body'
                entry={'path':str(directory.relative_to(root)),'http_status':status,'terminal':[x for x in events if x.get('kind') in ['end','failure','rejected']]}
                try:
                    if status!=200 or not body.exists():raise ValueError('failed or missing response')
                    stream=parse(body)
                    if len(stream['response_ids'])!=1 or not stream['terminal_marker'] or stream['late_data']:raise ValueError('incomplete/ambiguous stream')
                    ident=stream['response_ids'][0]
                    if ident in target:raise ValueError('duplicate response capture')
                    target[ident]={'entry':entry,'parsed':stream}
                except (ValueError,OSError) as error:
                    unknown.append({**entry,'view':kind,'usage':None,'reported_cost_usd':None,'reason':str(error)})
        billed=[];wire=[]
        for ident,item in providers.items():
            stream=item['parsed'];gateway=gateways.get(ident);usage=stream['usage'][-1] if stream['usage'] else None
            matched=gateway is not None and stream['semantic']==gateway['parsed']['semantic']
            wire.append({'response_id':ident,'gateway_pair_present':gateway is not None,'semantic_fidelity':matched})
            if not isinstance(usage,dict):unknown.append({'response_id':ident,'view':'provider','reason':'usage unavailable','usage':None});continue
            required=[usage.get('prompt_tokens'),usage.get('completion_tokens')]
            if any(type(n) is not int or n<0 for n in required):unknown.append({'response_id':ident,'reason':'invalid required counters','usage':usage});continue
            canonical=json.dumps(usage,sort_keys=True,allow_nan=False)
            if ident in seen:
                if seen[ident]!=(role,canonical):raise ValueError('conflicting cross-role/usage response identity')
                continue
            seen[ident]=(role,canonical)
            prompt_details=usage.get('prompt_tokens_details') or {};completion_details=usage.get('completion_tokens_details') or {}
            for field,value in [('cached_tokens',prompt_details.get('cached_tokens')),('cache_write_tokens',prompt_details.get('cache_write_tokens',prompt_details.get('cache_creation_tokens'))),('reasoning_tokens',completion_details.get('reasoning_tokens'))]:
                if value is not None and (type(value) is not int or value<0):unknown.append({'response_id':ident,'reason':'invalid optional counter '+field,'usage':usage})
            cost=usage.get('cost')
            if cost is not None and (type(cost) not in (int,float) or not math.isfinite(cost) or cost<0):unknown.append({'response_id':ident,'reason':'invalid reported cost','usage':usage})
            billed.append({'response_id':ident,'input_inclusive':usage['prompt_tokens'],'output_billable_completion':usage['completion_tokens'],
                'cached_input_subset':prompt_details.get('cached_tokens'),'cache_write_subset':prompt_details.get('cache_write_tokens',prompt_details.get('cache_creation_tokens')),
                'reasoning_diagnostic_not_added':completion_details.get('reasoning_tokens'),'reported_cost_usd':cost if type(cost) in (int,float) and math.isfinite(cost) and cost>=0 else None,
                'raw_usage':usage,'usage_snapshots_observed':len(stream['usage']),'source':item['entry']['path']+'/response.body'})
        for ident in gateways.keys()-providers.keys():unknown.append({'response_id':ident,'reason':'provider view missing','usage':None})
        native_paths=[root/'captures/parent/native.jsonl'] if role!='worker' else sorted((root/'captures/worker').glob('*/native.jsonl'))
        native={};sessions=set()
        for path in native_paths:
            if not path.exists():continue
            for event in rows(path):
                if event.get('sessionID'):sessions.add(event['sessionID'])
                if event.get('type')!='step_finish':continue
                part=event.get('part',{});ident=part.get('id')
                if not ident:unknown.append({'reason':'native step has no stable ID','usage':None});continue
                payload={'session_id':event.get('sessionID'),'part':part,'source':str(path.relative_to(root))}
                if ident in native and native[ident]['part']!=part:raise ValueError('conflicting stable native step ID')
                native[ident]=payload
        def total(key):
            values=[row.get(key) for row in billed]
            return sum(values) if values and all(type(x) in (int,float) for x in values) else None
        result.append({'role':role,'native_session_ids':sorted(sessions),'provider_successful_generations':len(billed),'native_unique_steps':len(native),
            'successful_wire_pairs':sum(x['semantic_fidelity'] for x in wire),'wire_checks':wire,'provider_billing_records':billed,
            'known_input_inclusive_total':total('input_inclusive'),'known_billable_output_total':total('output_billable_completion'),
            'cached_input_subset_total':total('cached_input_subset'),'cache_write_subset_total':total('cache_write_subset'),
            'diagnostic_reasoning_total':total('reasoning_diagnostic_not_added'),'known_reported_cost_usd_subtotal':total('reported_cost_usd'),
            'native_diagnostics':list(native.values()),'unknown_attempts_or_views':unknown,
            'all_successes_have_native_step_count_match':len(native)==len(billed),'cost_complete':not unknown and bool(billed) and total('reported_cost_usd') is not None,
            'limits':'Native/provider per-call attribution and any non-step compaction require separate reconciliation; no count mismatch is silently repaired. Provider resolution requires actual response/catalog/generation evidence.'})
    return {'kind':'offline_raw_pilot_usage_summary_not_acceptance_or_dispatch_approval','roles':result,
        'physical_billable_generations_counted_once':len(seen),'billing_source':'final raw provider usage only; gateway/native are cross-checks, never additional charges',
        'reasoning_rule':'not added to completion','missing_rule':'unknown remains null; known subtotal is not a complete invoice'}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('root',type=Path);parser.add_argument('--output',required=True,type=Path);args=parser.parse_args()
    if args.output.exists():raise ValueError('Preserve the earlier summary; use a new output')
    report=summarize(args.root);args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'roles':len(report['roles']),'provider_generations_once':report['physical_billable_generations_counted_once'],'output':str(args.output)}))

if __name__=='__main__':main()
