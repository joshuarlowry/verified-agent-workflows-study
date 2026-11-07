"""Replay baseline public checks in independent, offline disposable containers.

Runtime preparation evidence only: this is not task acceptance or full study
qualification. The source snapshot, image inputs and every exit code are kept.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import tempfile
import time
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--source-baseline',required=True,type=Path)
p.add_argument('--source-snapshot',required=True,type=Path)
p.add_argument('--image-record',required=True,type=Path)
p.add_argument('--instances',type=int,default=3)
p.add_argument('--record',required=True,type=Path)
p.add_argument('--apparmor-profile',required=True)
a=p.parse_args()
source=a.source_baseline.resolve();output=(ROOT/a.record).resolve()
private=Path('/home/josh/.local/state/study2-setup').resolve()
if not (source.is_relative_to(ROOT) or source.is_relative_to(private)) or not 1<=a.instances<=3:
    raise ValueError('Invalid local source/instance count')
if not output.is_relative_to(ROOT/'setup') or output.exists():
    raise ValueError('Use a new setup record path; preserve prior endpoints')
if a.apparmor_profile!=json.loads((ROOT/'harness/security/profile-source.json').read_text())['profile_name']:
    raise ValueError('Only the study-local candidate profile is supported')
snapshot=json.loads(a.source_snapshot.read_text())['files_sha256']
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
for name,digest in snapshot.items():
    path=(source/name).resolve()
    if not path.is_relative_to(source) or not path.is_file() or sha(path)!=digest:
        raise ValueError('Source snapshot mismatch: '+name)
image=json.loads((ROOT/a.image_record).read_text())
if image.get('exit_code')!=0 or image.get('version_manifest_exit_code')!=0 or not image.get('image_id'):
    raise ValueError('Dependency image did not pass build/version capture')
for file,field in [('package-lock.json','application_lock_sha256'),('package.json','application_package_sha256')]:
    if sha(source/file)!=image['input_hashes'][field]:raise ValueError('Image inputs differ from source')
records=private/'baseline-container-replays';records.mkdir(exist_ok=True)
run=records/('replay-'+secrets.token_hex(6));run.mkdir();results=[]
for i in range(a.instances):
    start=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat();name='study2-baseline-'+secrets.token_hex(5)
    row={'instance':i+1,'dispatch_utc':utc,'commands':[],'error':None}
    with tempfile.TemporaryDirectory(prefix='study2-app-replay-') as temp:
        workspace=Path(temp)/'workspace';workspace.mkdir()
        for relative in snapshot:
            target=workspace/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source/relative,target)
        if os.geteuid()==0:
            for f in [workspace,*workspace.rglob('*')]:os.chown(f,1000,1000)
        command=['sudo','-n','podman','run','--detach','--init','--name',name,'--network','none','--read-only','--tmpfs','/tmp:rw,nosuid,nodev,size=1g','--memory','8g','--memory-swap','8g','--cpuset-cpus','0,1','--pids-limit','256','--cap-drop','ALL','--security-opt','no-new-privileges','--security-opt','apparmor='+a.apparmor_profile,'--user','1000:1000','-e','HOME=/home/node','-e','PWD=/workspace','-e','npm_config_cache=/workspace/.npm-cache','-v',f'{workspace}:/workspace:rw','--workdir','/workspace',image['image_id'],'node','-e','setInterval(()=>{},10000)']
        try:
            launched=subprocess.run(command,capture_output=True,text=True)
            if launched.returncode:raise RuntimeError('Container launch: '+launched.stderr)
            prepared=subprocess.run(['sudo','-n','podman','exec',name,'cp','-R','/opt/application-deps/node_modules','/workspace/node_modules'],capture_output=True,text=True)
            row['preparation_seconds']=time.monotonic()-start
            if prepared.returncode:raise RuntimeError('Dependency copy: '+prepared.stderr)
            probe="console.log(JSON.stringify({node:process.version,cpus:require('node:os').availableParallelism(),sqlite:require('better-sqlite3')(':memory:').prepare('select sqlite_version() as version').get().version,nodeEnv:process.env.NODE_ENV??null,testEnv:process.env.TEST??null}))"
            commands=[['node','-e',probe],['npm','--version'],['npm','run','build'],['npm','run','typecheck'],['npm','run','lint'],['npm','test'],['npm','run','e2e'],['npm','run','reset']]
            for j,cmd in enumerate(commands,1):
                at=time.monotonic();checked=subprocess.run(['sudo','-n','podman','exec','--workdir','/workspace',name,*cmd],capture_output=True,text=True)
                (run/f'instance-{i+1}-command-{j}.stdout.log').write_text(checked.stdout)
                (run/f'instance-{i+1}-command-{j}.stderr.log').write_text(checked.stderr)
                row['commands'].append({'argv':cmd,'exit_code':checked.returncode,'elapsed_seconds':time.monotonic()-at,'stdout_sha256':hashlib.sha256(checked.stdout.encode()).hexdigest(),'stderr_sha256':hashlib.sha256(checked.stderr.encode()).hexdigest()})
                if checked.returncode:break
            row['source_unchanged']=all(sha(workspace/rel)==digest for rel,digest in snapshot.items())
        except Exception as e:
            row['error']=str(e)
        finally:
            cleanup=subprocess.run(['sudo','-n','podman','rm','-f','-t','0',name],capture_output=True,text=True)
            row['cleanup_exit_code']=cleanup.returncode
    row['total_elapsed_seconds_including_cleanup']=time.monotonic()-start
    row['passed']=row['error'] is None and len(row['commands'])==8 and all(c['exit_code']==0 for c in row['commands']) and row.get('source_unchanged') and row['cleanup_exit_code']==0
    results.append(row)
    (run/f'instance-{i+1}.json').write_text(json.dumps(row,indent=2)+'\n')
report={'kind':'clean_container_public_regression_replay_not_task_acceptance_or_full_qualification','model_calls':0,'source_snapshot_sha256':sha(a.source_snapshot),'source_files':len(snapshot),'application_lock_sha256':sha(source/'package-lock.json'),'image_id':image['image_id'],'resource_limits':{'cpu_mask':'0,1','memory_bytes':8589934592,'pids':256,'network':'none','rootfs':'read_only','apparmor_profile':a.apparmor_profile},'independent_dependencies':'Separate writable copies of dependencies, source, SQLite files, browser profiles, build and TypeScript caches; no writable node_modules symlinks. npm ci ran during image build before copying dependencies.','instances':results,'all_public_checks_passed':all(r['passed'] for r in results),'qualification_limits':['Native API unit tests remain test-mode conditional; trusted evaluator non-test auth probes are separate.','No sealed task acceptance, reference/alternate implementations or negative controls.','No concurrent lanes, live models, Context or worker broker qualification.','Study-local signal profile and dependency image still need current different-model final-runtime review.']}
output.write_text(json.dumps(report,indent=2)+'\n');(run/'controller.json').write_text(json.dumps(report,indent=2)+'\n')
if os.geteuid()==0:os.chown(output,1000,1000)
print(json.dumps({'record':str(a.record),'all_public_checks_passed':report['all_public_checks_passed'],'instances':len(results),'image_id':image['image_id']}))
if not report['all_public_checks_passed']:raise SystemExit(1)
