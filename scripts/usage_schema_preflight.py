"""Adversarial mechanical cases from the preparation cross-review; no model API."""
import copy
import json
from pathlib import Path
import sys
import jsonschema
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'harness'))
from normalize_usage import normalize,deduplicate,ReconciliationError
base=dict(run_id='run',session_id='session',actor_role='coordinator',requested_model='z-ai/glm-5.3-flash',response_id='synthetic-case',mapping_id='glm-relace-completion-only-r7',provider_tag='relace/fp4',phase='mechanical_preflight')
schema=json.loads((ROOT/'schemas/provider-usage-record.schema.json').read_text());checks={}
def row(usage,**changes):return normalize(usage,**{**base,**changes})
def rejected(function):
    try:function()
    except ValueError:return True
    return False
usage={'prompt_tokens':19,'completion_tokens':89,'completion_tokens_details':{'reasoning_tokens':104},'prompt_tokens_details':{'cache_write_tokens':7,'cache_creation_tokens':7},'cost':0.0000087543}
r=row(usage);jsonschema.validate(r,schema);checks['reasoning_not_added']=r['billing_counters']['billable_output_tokens']==89 and r['billing_counters']['diagnostic_reasoning_tokens']==104
checks['equal_write_alias_once']=r['billing_counters']['cache_write_tokens']==7
checks['alias_conflict_rejected']=rejected(lambda:row({'prompt_tokens_details':{'cache_write_tokens':0,'cache_creation_tokens':7}}))
checks['bad_nested_types_rejected']=rejected(lambda:row({'completion_tokens_details':[]}))
checks['negative_and_nonfinite_cost_rejected']=all(rejected(lambda value=value:row({'cost':value})) for value in [-1,float('nan'),float('inf')])
checks['metadata_and_mapping_rejected']=all(rejected(lambda changes=changes:row({},**changes)) for changes in [{'actor_role':'invented'},{'phase':'invented'},{'mapping_id':'invented'},{'provider_tag':'other'},{'requested_model':'openai/gpt-6.1-terra'}])
a=row({},run_id='a:b',session_id='c');b=row({},run_id='a',session_id='b:c');checks['tuple_ids_unambiguous']=a['record_id']!=b['record_id']
checks['cross_session_same_response_not_double_charged']=rejected(lambda:deduplicate([a,b]))
checks['identical_duplicate_once']=len(deduplicate([r,r]))==1
incomplete=row({});merged=deduplicate([r,incomplete])[0];jsonschema.validate(merged,schema)
checks['incomplete_duplicate_retains_known_and_raw']=merged['billing_counters']['billable_output_tokens']==89 and len(merged['raw_provider_usage_snapshots'])==2 and bool(merged['normalization_warnings'])
checks['conflicting_final_counter_rejected']=rejected(lambda:deduplicate([r,row({'completion_tokens':90})]))
missing=row({});checks['missing_stays_null']=all(value is None for value in missing['billing_counters'].values())
checks['invalid_metadata_type_rejected']=rejected(lambda:row({},actor_role=[]))
checks['invalid_unused_alias_type_rejected']=rejected(lambda:row({'prompt_tokens_details':{'cache_write_tokens':0,'cache_creation_tokens':False}}))
changed=copy.deepcopy(r);changed['source']='unregistered'
checks['unregistered_source_rejected']=rejected(lambda:deduplicate([changed]))
checks['input_not_mutated']=usage['completion_tokens_details']['reasoning_tokens']==104 and 'raw_provider_usage_snapshots' not in usage
report={'kind':'mechanical_adversarial_usage_probe_not_model_evaluation','model_calls':0,'checks':checks,'all_passed':all(checks.values()),'remaining':'different-model review, all-model mappings and full broker/capture/ancestry integration'}
(ROOT/'setup/usage-schema-revision2.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if not report['all_passed']:raise SystemExit(1)
