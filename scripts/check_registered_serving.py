"""Read-only provider metadata checks; never infer, reroute or change settings."""
import datetime
import json
from pathlib import Path
import time
import urllib.error
import urllib.parse
import urllib.request

API = 'https://openrouter.ai/api/v1'


def read_json(url, key=None):
    headers = {'Accept':'application/json'}
    if key is not None:
        headers['Authorization'] = 'Bearer '+key
    with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=30) as response:
        return json.load(response)


def write(path, value):
    path = Path(path)
    if path.exists():
        raise ValueError('Preserve previous provider metadata evidence')
    path.write_text(json.dumps(value,indent=2)+'\n')


def preflight(models, directory):
    directory = Path(directory);directory.mkdir(mode=0o700)
    catalog = read_json(API+'/models')
    write(directory/'catalog.json',catalog)
    rows = []
    for index, model in enumerate(models):
        matches = [x for x in catalog['data'] if x['id']==model['requested_id']]
        if len(matches)!=1 or matches[0].get('canonical_slug')!=model['resolved_id']:
            raise ValueError('Public canonical model changed or disappeared: '+model['name'])
        endpoints = read_json(API+'/models/'+model['resolved_id']+'/endpoints')
        write(directory/('endpoints-'+str(index)+'.json'),endpoints)
        selected = [x for x in endpoints['data']['endpoints'] if x.get('tag')==model['provider_tag']]
        if len(selected)!=1 or selected[0].get('provider_name')!=model['provider']:
            raise ValueError('Registered provider tag/name changed or disappeared: '+model['name'])
        endpoint = selected[0]
        if model['quantization']!='not_disclosed' and endpoint.get('quantization')!=model['quantization']:
            raise ValueError('Public serving precision changed: '+model['name'])
        if not endpoint.get('supports_tool_choice',{}).get('auto') or endpoint.get('context_length',0)<200000 or endpoint.get('max_completion_tokens',0)<16384:
            raise ValueError('Registered tool/context/output availability changed: '+model['name'])
        rows.append({'requested_id':model['requested_id'],'canonical_slug':matches[0]['canonical_slug'],
                     'provider_tag':endpoint['tag'],'provider':endpoint['provider_name'],'quantization':endpoint.get('quantization')})
    record = {'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'rows':rows,
              'model_calls':0,'status':'public_metadata_matches',
              'limits':'Public listing is not inference availability or physical-weight attestation. ZDR and no-fallback are enforced by the qualified request adapter; actual dated model/provider is checked after calls.'}
    write(directory/'preflight.json',record)
    return record


def postflight(root, models_by_role, key_path):
    from summarize_workflow_capture import summarize
    root = Path(root);out=root/'provider-resolution';out.mkdir(mode=0o700)
    usage = summarize(root);write(out/'raw-usage-summary.json',usage)
    key = Path(key_path).read_text().strip()
    if not key:
        raise ValueError('Provider metadata credential unavailable')
    rows = []; errors = []; measurement_gaps = []
    for role in usage['roles']:
        model = models_by_role[role['role']]
        if role['unknown_attempts_or_views']:
            measurement_gaps.append({'role':role['role'],'kind':'failed_or_unknown_usage_views',
                                     'views':role['unknown_attempts_or_views']})
        if any(not pair['semantic_fidelity'] for pair in role['wire_checks']):
            errors.append({'role':role['role'],'kind':'successful_generation_wire_fidelity_unverified'})
        for generation in role['provider_billing_records']:
            ident=generation['response_id'];attempts=[];document=None
            for attempt in range(5):
                try:
                    document=read_json(API+'/generation?id='+urllib.parse.quote(ident,safe=''),key)
                    attempts.append({'attempt':attempt+1,'status':200});break
                except urllib.error.HTTPError as exc:
                    attempts.append({'attempt':attempt+1,'http_status':exc.code})
                    if exc.code==404 and attempt<4:
                        time.sleep(2);continue
                    break
                except (OSError,ValueError) as exc:
                    attempts.append({'attempt':attempt+1,'error_type':type(exc).__name__});break
            write(out/('generation-'+str(len(rows))+'.json'),{'response_id':ident,'attempts':attempts,'document':document})
            actual = document.get('data',{}) if isinstance(document,dict) else {}
            matches = actual.get('model')==model['resolved_id'] and actual.get('provider_name')==model['provider']
            row={'role':role['role'],'response_id':ident,'resolved_model':actual.get('model'),'provider':actual.get('provider_name'),
                 'expected_model':model['resolved_id'],'expected_provider':model['provider'],'matches':matches}
            rows.append(row)
            if not matches:
                errors.append({'role':role['role'],'response_id':ident,'kind':'actual_resolution_mismatch_or_unavailable'})
    if not rows:
        errors.append({'kind':'no_successful_provider_generations_to_verify'})
    record={'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'model_calls':0,
            'status':'verified' if not errors else 'unverified_or_drift_stop_new_dispatch','rows':rows,'errors':errors,
            'measurement_gaps':measurement_gaps,
            'scope':'Administrative metadata cross-checks only; costs/tokens are not added to raw provider usage and no implementation quality is inspected.'}
    write(out/'verification.json',record)
    if errors:
        raise ValueError('Actual provider resolution or capture unverified; stop new dispatch')
    return record
