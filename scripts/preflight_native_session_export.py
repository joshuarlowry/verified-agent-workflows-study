"""Offline native session identity/export probe; no inference socket or API calls."""
import datetime
import hashlib
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import time

REPO = Path(__file__).resolve().parents[1]
PRIVATE = Path('/home/josh/.local/state/study2-setup')
COHORT = PRIVATE/'clean-20261107T122746Z'
SOURCE_HOME = COHORT/'native-worker-short-socket-20261107T220933Z/home'
OWNED_SESSION = 'ses_e47edd643ffeMBBgGhFDpZKRjK'
IMAGE = '3005436d2c76060957f7944203f2edb281a1ffb33f16e8a85cc68444dfb5ef38'


def main():
    if os.geteuid() != 0:
        raise SystemExit('Requires authorized preparation controller')
    job = COHORT/('native-session-export-'+datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
    job.mkdir()
    shutil.copy2(__file__, job/'controller-source.py')
    home = job/'home'
    shutil.copytree(SOURCE_HOME, home, symlinks=True)
    workspace = job/'workspace'; workspace.mkdir()
    for p in [home, *home.rglob('*'), workspace]: os.lchown(p, 1000, 1000)
    name = 'study2-session-export-'+secrets.token_hex(5)
    started = time.monotonic()
    report = {'kind':'offline_native_session_export_mechanical_probe_not_role_qualification',
              'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'model_calls':0,
              'image_id':IMAGE, 'existing_session_source':'Disposable transport-only two-handoff Gemma probe; fresh copy of its home, no app/task or prior solution.',
              'original_session_home_modified':False, 'inference_socket_mounted':False, 'commands':[]}
    def command(argv):
        at = time.monotonic()
        p = subprocess.run(argv, capture_output=True, text=True, timeout=60)
        index = len(report['commands'])+1
        (job/f'command-{index}.stdout.log').write_text(p.stdout)
        (job/f'command-{index}.stderr.log').write_text(p.stderr)
        report['commands'].append({'argv':argv,'exit_code':p.returncode,'elapsed_seconds':time.monotonic()-at,
                                  'stdout_sha256':hashlib.sha256(p.stdout.encode()).hexdigest(),
                                  'stderr_sha256':hashlib.sha256(p.stderr.encode()).hexdigest()})
        return p
    def native(*args): return command(['podman','exec',name,'opencode',*args])
    try:
        p = command(['podman','run','--detach','--init','--name',name,'--network','none','--read-only',
                     '--tmpfs','/tmp:rw,nosuid,nodev,size=1g','--memory','8g','--memory-swap','8g','--cpuset-cpus','2,3',
                     '--pids-limit','256','--cap-drop','ALL','--security-opt','no-new-privileges',
                     '--security-opt','apparmor=study2-agent-a5ccdae8-stack1','--user','1000:1000',
                     '-e','HOME=/home/node','-e','PWD=/workspace','-v',str(home)+':/home/node:rw',
                     '-v',str(workspace)+':/workspace:rw','--workdir','/workspace',IMAGE,
                     'node','-e','setInterval(()=>{},10000)'])
        if p.returncode: raise RuntimeError('Container launch failed')
        before = native('session','list','--standalone','--format','json')
        existing = native('session','export','--standalone',OWNED_SESSION)
        missing_id = 'ses_study2missing'+secrets.token_hex(8)
        missing = native('session','export','--standalone',missing_id)
        after = native('session','list','--standalone','--format','json')
        exported = json.loads(existing.stdout) if existing.returncode==0 else None
        before_data = json.loads(before.stdout) if before.returncode==0 else None
        after_data = json.loads(after.stdout) if after.returncode==0 else None
        report['existing_export'] = {'exit_code':existing.returncode,
            'top_level_keys':list(exported) if isinstance(exported,dict) else None,
            'top_level_info_id':exported.get('info',{}).get('id') if isinstance(exported,dict) else None,
            'messages':len(exported.get('messages',[])) if isinstance(exported,dict) else None}
        report['missing_export'] = {'exit_code':missing.returncode,'stdout_bytes':len(missing.stdout.encode()),
                                    'stderr_bytes':len(missing.stderr.encode())}
        report['checks'] = {'existing_export_has_expected_identity':isinstance(exported,dict) and exported.get('info',{}).get('id')==OWNED_SESSION,
                            'missing_export_rejected':missing.returncode!=0,
                            'list_before_after_succeeded':before.returncode==after.returncode==0,
                            'session_list_unchanged':before_data==after_data}
        report['all_passed'] = all(report['checks'].values())
    except BaseException as exc:
        report.update(all_passed=False,error_type=type(exc).__name__,error=str(exc))
    finally:
        cleanup = command(['podman','rm','-f','-t','0',name])
        report['cleanup_exit_code'] = cleanup.returncode
        report['all_passed'] = report.get('all_passed',False) and cleanup.returncode==0
        report['elapsed_seconds'] = time.monotonic()-started
        report['scope'] = 'Actual CLI export/list identity and missing-session behavior only. Does not prove atomic session continuation, broker ownership, native event semantics, sandbox escape resistance, or seven-role/Context qualification.'
        (job/'controller.json').write_text(json.dumps(report,indent=2)+'\n')
        public = REPO/'setup/native-session-export-preflight.json'
        public.write_text(json.dumps(report,indent=2)+'\n'); os.chown(public,1000,1000)
        print(json.dumps({'job':str(job),'all_passed':report['all_passed']}))
    if not report['all_passed']: raise SystemExit(1)


if __name__=='__main__': main()
