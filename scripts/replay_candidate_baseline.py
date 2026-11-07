"""Replay the builder's public check in isolated fresh local containers.

This is runtime preparation evidence, never a task-acceptance result. Every
instance owns its dependency copy, SQLite files, build output, browser profiles
and loopback network. Requires a newly built, recorded dependency image.
"""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import secrets
import shutil
import subprocess
import tempfile
import time
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--instances',type=int,default=1);p.add_argument('--record',required=True);p.add_argument('--apparmor-profile');a=p.parse_args()
source=(ROOT/a.source/'baseline').resolve();output=ROOT/a.record
if output.exists():raise ValueError('Use a new record path; preserve prior endpoints')
if not source.is_relative_to(ROOT) or not 1<=a.instances<=3:raise ValueError('Invalid local source/instance count')
image=json.loads((ROOT/'setup/image-build-preliminary.json').read_text())
for file,field in [('package-lock.json','application_lock_sha256'),('package.json','application_package_sha256')]:
    if hashlib.sha256((source/file).read_bytes()).hexdigest()!=image['input_hashes'][field]:raise ValueError('Dependency image inputs differ from source')
private=Path('/home/josh/.local/state/study2-setup/baseline-container-replays');private.mkdir(exist_ok=True)
run=private/('replay-'+secrets.token_hex(6));run.mkdir();results=[]
for i in range(a.instances):
    start=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat();name='study2-baseline-'+secrets.token_hex(5)
    with tempfile.TemporaryDirectory(prefix='study2-app-replay-') as temp:
        workspace=Path(temp)/'workspace';shutil.copytree(source,workspace,ignore=shutil.ignore_patterns('node_modules','.tmp','dist','test-results','playwright-report','*.tsbuildinfo'))
        command=['sudo','-n','podman','run','--detach','--init','--name',name,'--network','none','--read-only','--tmpfs','/tmp:rw,nosuid,nodev,size=1g','--memory','8g','--memory-swap','8g','--cpuset-cpus','0,1','--pids-limit','256','--cap-drop','ALL','--security-opt','no-new-privileges',*(['--security-opt','apparmor='+a.apparmor_profile] if a.apparmor_profile else []),'--user','1000:1000','-e','HOME=/home/node','-e','PWD=/workspace','-v',f'{workspace}:/workspace:rw','--workdir','/workspace',image['image_id'],'node','-e','setInterval(()=>{},10000)']
        try:
            launched=subprocess.run(command,capture_output=True,text=True)
            if launched.returncode:raise RuntimeError(launched.stderr)
            prepared=subprocess.run(['sudo','-n','podman','exec',name,'cp','-R','/opt/application-deps/node_modules','/workspace/node_modules'],capture_output=True,text=True)
            prepared_elapsed=time.monotonic()-start
            if prepared.returncode:raise RuntimeError(prepared.stderr)
            test_start=time.monotonic()
            checked=subprocess.run(['sudo','-n','podman','exec','--workdir','/workspace',name,'npm','run','check:full'],capture_output=True,text=True)
            test_elapsed=time.monotonic()-test_start
            (run/f'instance-{i+1}.stdout.log').write_text(checked.stdout)
            (run/f'instance-{i+1}.stderr.log').write_text(checked.stderr)
            results.append({'instance':i+1,'dispatch_utc':utc,'preparation_seconds':prepared_elapsed,'public_check_seconds':test_elapsed,'exit_code':checked.returncode,'stdout_sha256':hashlib.sha256(checked.stdout.encode()).hexdigest(),'stderr_sha256':hashlib.sha256(checked.stderr.encode()).hexdigest()})
        finally:
            subprocess.run(['sudo','-n','podman','rm','-f','-t','0',name],capture_output=True)
        results[-1]['total_elapsed_seconds_including_container_cleanup']=time.monotonic()-start
report={'kind':'clean_container_public_regression_replay_not_task_acceptance_or_full_qualification','model_calls':0,'source':a.source,'image_id':image['image_id'],'resource_limits':{'assigned_cpu_mask':'0,1','memory_bytes':8589934592,'pids':256,'network':'none','rootfs':'read_only','apparmor_profile':a.apparmor_profile or 'runtime_default'},'independent_dependencies':'copied separately into each fresh writable workspace; no writable shared node_modules links','instances':results,'all_public_checks_passed':all(r['exit_code']==0 for r in results),'qualification_limits':['baseline/contract cross-review is separate','no sealed task acceptance or positive/negative controls','no concurrent lane, actual model, Context or broker runtime qualification']}
output.write_text(json.dumps(report,indent=2)+'\n');(run/'controller.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if not report['all_public_checks_passed']:raise SystemExit(1)
