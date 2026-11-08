"""Compose frozen C1 checks after timed collection; no oracle or subject edits.

Reads immutable first endpoints, stages source-only copies, and invokes the
already-qualified checkers unchanged. This never starts or continues an agent.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import sqlite3
import stat
import subprocess
import sys
import time

REPO=Path(__file__).resolve().parents[1]
PRIVATE=Path('/home/josh/.local/state/study2-setup').resolve()
GENERATED={'.git','node_modules','data','dist','.npm-cache','.cache','test-results','playwright-report','.vite'}
OVERLAY={'STUDY_TASK.md','STUDY_FAQ.md','baseline-spec.md'}
IMAGE='3005436d2c76060957f7944203f2edb281a1ffb33f16e8a85cc68444dfb5ef38'
PROFILE='study2-agent-a5ccdae8-stack1'

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def load(path):return json.loads(path.read_text())
def write(path,value):path.write_text(json.dumps(value,indent=2)+'\n')

def check_frozen(path,expected):
    if not path.is_relative_to(PRIVATE) or path.is_symlink() or path.stat().st_uid!=0 or path.stat().st_mode&0o022 or sha(path)!=expected:
        raise ValueError('Protected manifest changed')
    return load(path)

def copy_inventory(source,files,dest):
    dest.mkdir(mode=0o755)
    for name,digest in files.items():
        relative=Path(name)
        if relative.is_absolute() or '..' in relative.parts:raise ValueError('Unsafe source inventory path')
        p=source/relative
        if p.is_symlink() or not p.resolve().is_relative_to(source) or not p.is_file() or sha(p)!=digest:raise ValueError('Source inventory mismatch: '+name)
        out=dest/relative;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out);out.chmod(0o444)
    for p in dest.rglob('*'):
        if p.is_dir():p.chmod(0o755)

def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--block',required=True,type=Path);args=a.parse_args()
    if os.geteuid()!=0:raise SystemExit('Root controller required')
    block=args.block.resolve(strict=True)
    if not block.is_relative_to(PRIVATE) or block.stat().st_uid!=0:raise ValueError('Protected study block required')
    state=load(block/'collection.json')
    if state['status']=='running':raise ValueError('No heavy grading during timed collection')
    db=sqlite3.connect((block/'study-ledger.sqlite').as_uri()+'?mode=ro',uri=True)
    try:
        if db.execute("SELECT 1 FROM runs WHERE state='active'").fetchone():raise ValueError('A subject is still active')
    finally:db.close()
    reg=load(block/'frozen-registration.json');manifests={}
    for record in reg['calibration_initial_block']['frozen_manifests']:
        manifests[record['category']]=check_frozen(Path(record['path']),record['sha256'])
    acceptance=manifests['acceptance'];checker=Path(acceptance['source']);baseline=Path(manifests['baseline']['source'])
    if manifests['image']['image_id']!=IMAGE or sha(Path(manifests['image']['source_record']))!=manifests['image']['source_record_sha256']:
        raise ValueError('Frozen image identity or record changed')
    if sha(Path(acceptance['native_auth_probe']))!=acceptance['native_auth_probe_sha256']:raise ValueError('Auth probe changed')
    for name,digest in acceptance['files_sha256'].items():
        if sha(checker/name)!=digest:raise ValueError('Frozen acceptance package changed')
    grading=block/'grading-first-endpoints'
    if grading.exists():raise ValueError('Preserve first grading; a later extension needs separate tooling/state')
    grading.mkdir(mode=0o700)
    baseline_copy=grading/'baseline';copy_inventory(baseline,manifests['baseline']['files_sha256'],baseline_copy)
    checker_copy=grading/'checker';copy_inventory(checker,acceptance['files_sha256'],checker_copy)
    (checker_copy/'node_modules').symlink_to('/opt/application-deps/node_modules')
    checker_inventory=grading/'checker-inventory.json';write(checker_inventory,{'files_sha256':acceptance['files_sha256']})
    report={'kind':'first_endpoint_frozen_machine_grading','started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'block':str(block),'model_calls':0,'acceptance_manifest_sha256':sha(Path(next(x['path'] for x in reg['calibration_initial_block']['frozen_manifests'] if x['category']=='acceptance'))),
            'policy':'Timely final plus every frozen gate. Subject tests supplement independent tests; no semantic/human merge certification.','rows':[]}
    for row in state['runs']:
        runid=row['run_id'];root=Path(row['root']);out=grading/runid;out.mkdir(mode=0o700)
        result={'run_id':runid,'arm':row['arm'],'endpoint_reason':row.get('endpoint_reason'),'gates':{},'accepted':False,'commands':[]}
        def command(argv,label):
            at=time.monotonic();p=subprocess.run(argv,capture_output=True,text=True)
            (out/(label+'.stdout.log')).write_text(p.stdout);(out/(label+'.stderr.log')).write_text(p.stderr)
            result['commands'].append({'label':label,'argv':argv,'exit_code':p.returncode,'elapsed_seconds':time.monotonic()-at,
                                       'stdout_sha256':hashlib.sha256(p.stdout.encode()).hexdigest(),'stderr_sha256':hashlib.sha256(p.stderr.encode()).hexdigest()})
            return p
        try:
            receipt=load(root/'endpoint.json');quiescence=load(root/'endpoint.json.quiescence.json')
            if receipt['status']!='copied_and_empty_unqualified' or quiescence.get('pod_empty_after_quiescence') is not True:raise ValueError('Endpoint freeze/quiescence not proven')
            endpoint=Path(receipt['destination']);source=out/'source';source.mkdir(mode=0o755);files={};overlay={}
            for name,entry in receipt['manifest'].items():
                relative=Path(name)
                if name=='.' or relative.parts[0] in GENERATED:continue
                if relative.is_absolute() or '..' in relative.parts:raise ValueError('Unsafe endpoint entry')
                p=endpoint/relative
                if entry['type']=='directory':continue
                if entry['type']!='file' or p.is_symlink() or not stat.S_ISREG(p.lstat().st_mode) or sha(p)!=entry['sha256']:
                    raise ValueError('Nonregular or changed application endpoint entry: '+name)
                if name in OVERLAY:
                    if sha(p)!=manifests['baseline']['overlay'][name]:raise ValueError('Frozen task overlay changed')
                    overlay[name]=sha(p);continue
                target=source/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target);target.chmod(0o444);files[name]=entry['sha256']
            if set(overlay)!=OVERLAY:raise ValueError('Task overlay missing')
            for p in source.rglob('*'):
                if p.is_dir():p.chmod(0o755)
            snapshot=out/'source-inventory.json';write(snapshot,{'files_sha256':files,'endpoint_receipt_sha256':sha(root/'endpoint.json'),'generated_root_exclusions':sorted(GENERATED),'unchanged_overlay_omitted':overlay})
            result['gates']['endpoint_integrity']='pass'
            result['gates']['timely_final']='pass' if row.get('endpoint_reason')=='final' and row.get('native_exit_code')==0 else 'fail'
            core=['podman','run','--rm','--network','none','--read-only','--cap-drop','ALL','--security-opt','no-new-privileges','--security-opt','apparmor='+PROFILE,'--user','1000:1000','--cpuset-cpus','2,3','--memory','8g','--memory-swap','8g','-v',str(checker_copy)+':/checker:ro','-v',str(baseline_copy)+':/baseline:ro','-v',str(source)+':/target:ro','--workdir','/checker',IMAGE,'node','source-scope/core.mjs','/baseline','/target']
            p=command(core,'source-scope');result['gates']['finite_source_preservation']='pass' if p.returncode==0 else 'fail'
            result['source_rule_limit']='A rejection can be an unsupported transformation under the frozen finite relation; it is not proof of semantic software incorrectness.'
            for suite in ['all','regression']:
                p=command([sys.executable,str(REPO/'scripts/replay_external_evaluator.py'),'--target',str(source),'--target-inventory',str(snapshot),'--evaluator',str(checker),'--evaluator-inventory',str(checker_inventory),'--format','playwright','--suite',suite,'--bind-disposable-db'],'external-'+suite)
                lines=p.stdout.strip().splitlines();detail=load(Path(json.loads(lines[-1])['receipt'])) if lines else {}
                complete=p.returncode==0 and detail.get('plumbing_completed') and detail.get('standard_inventory_matches')
                key='feature_public_and_sealed' if suite=='all' else 'protected_baseline_regression'
                result['gates'][key]=('pass' if detail.get('native_runner_all_passed') else 'fail') if complete else 'unverified'
                result['gates'][suite+'_initial_db']=('pass' if detail['initial_db_gate']['exit_code']==0 else 'fail') if 'initial_db_gate' in detail else 'unverified'
                result['gates'][suite+'_post_schema']=('pass' if detail['post_test_db_gate']['exit_code']==0 else 'fail') if 'post_test_db_gate' in detail else 'unverified'
                result[key+'_receipt']=json.loads(lines[-1]).get('receipt') if lines else None
            for kind,script,field in [('app','replay_candidate_baseline.py','all_public_checks_passed'),('auth','replay_native_auth_binding.py','all_native_auth_probes_passed')]:
                name='c1-v2-'+runid+'-'+kind+'-first-grading.json';public_record=REPO/'setup'/name
                if public_record.exists():raise ValueError('Existing grading output must not be overwritten')
                cmd=[sys.executable,str(REPO/'scripts'/script),'--source-baseline',str(source),'--source-snapshot',str(snapshot),'--image-record',manifests['image']['source_record'],'--instances','1','--record',str(public_record),'--apparmor-profile',PROFILE]
                if kind=='auth':cmd+=['--probe-file',acceptance['native_auth_probe']]
                p=command(cmd,kind+'-checks');detail=load(public_record) if public_record.exists() else {}
                result['gates']['full_app_checks' if kind=='app' else 'native_auth_preservation']='pass' if p.returncode==0 and detail.get(field) is True else ('fail' if detail else 'unverified')
                result[kind+'_receipt']=str(public_record)
            result['gates']['post_grading_source_integrity']='pass' if all(sha(source/name)==digest for name,digest in files.items()) else 'fail'
            result['gates']['post_grading_checker_integrity']='pass' if all(sha(checker/name)==digest for name,digest in acceptance['files_sha256'].items()) and sha(Path(acceptance['native_auth_probe']))==acceptance['native_auth_probe_sha256'] else 'fail'
            result['accepted']=all(value=='pass' for value in result['gates'].values())
        except Exception as exc:
            result.update(error_type=type(exc).__name__,error=str(exc));result['gates'].setdefault('grading_complete','unverified')
        write(out/'result.json',result);report['rows'].append(result);write(grading/'report.json',report)
    report.update(ended_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),accepted_count=sum(x['accepted'] for x in report['rows']),first_endpoints_graded=len(report['rows']))
    write(grading/'report.json',report)
    print(json.dumps({'report':str(grading/'report.json'),'graded':len(report['rows']),'accepted':report['accepted_count'],'model_calls':0}))

if __name__=='__main__':main()
