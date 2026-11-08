"""Deterministic caller for the registered, separately admitted ten-slot C1 block.

No task selection, model feedback, quality inspection, repair or retry.  The
qualified native bootstrap owns clocks, first-return endpoints and cancellation.
This command cannot authorize itself: all seven protected manifests and the
registration admission must already exist and match their frozen hashes.
"""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
import threading
import time
from zoneinfo import ZoneInfo

PRIVATE = Path('/home/josh/.local/state/study2-setup').resolve()
IMAGE = '3005436d2c76060957f7944203f2edb281a1ffb33f16e8a85cc68444dfb5ef38'
REPO = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def protected(path):
    path = Path(path).resolve(strict=True)
    if not path.is_relative_to(PRIVATE) or path.stat().st_uid != 0 or path.stat().st_mode & 0o022:
        raise ValueError('Expected a protected private controller artifact')
    return path


def stamp():
    now = datetime.datetime.now(datetime.timezone.utc)
    return {'utc': now.isoformat(), 'eastern': now.astimezone(ZoneInfo('America/New_York')).isoformat(),
            'monotonic_ns': time.monotonic_ns()}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--registration', required=True, type=Path)
    p.add_argument('--block', required=True, type=Path)
    a = p.parse_args()
    if os.geteuid() != 0:
        raise SystemExit('Authorized root controller required')
    block = protected(a.block)
    with (block/'collection.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        registration_path = protected(a.registration)
        reg = json.loads(registration_path.read_text())
        admission = reg['calibration_initial_block']
        if admission.get('admitted') is not True or len(admission['order']) != 10:
            raise ValueError('The full registered C1 block has not been admitted')
        if (block/'collection.json').exists():
            raise ValueError('An existing collection endpoint/state must not be restarted')
        manifests = {}
        for record in admission['frozen_manifests']:
            path = protected(record['path'])
            if sha(path) != record['sha256']:
                raise ValueError('Frozen manifest mismatch')
            manifests[record['category']] = json.loads(path.read_text())
        if set(manifests) != {'baseline','image','harness','docs','acceptance','prompts','model_roles'}:
            raise ValueError('Incomplete frozen manifests')
        harness = protected(manifests['harness']['source'])
        for name, expected in manifests['harness']['files_sha256'].items():
            if sha(harness/name) != expected:
                raise ValueError('Frozen harness source mismatch: '+name)
        if manifests['image']['image_id'] != IMAGE:
            raise ValueError('Unregistered image')
        sys.path.insert(0, str(harness/'src'))
        from workflow_bootstrap import run_mechanical_workflow, validate_pilot_admission
        from core import Store
        staged = json.loads(protected(block/'prepared-workspaces.json').read_text())
        workspaces = {r['run_id']:r for r in staged['records']}
        docs = manifests['docs']
        context = {key: Path(docs[key]) for key in ['docs','docs_manifest','packages','package_manifest','approval']}
        context['expected_approval_sha256'] = docs['approval_sha256']
        public_checks = protected(manifests['acceptance']['public_checks'])
        prompts = manifests['prompts']
        for slot in admission['order']:
            workspace = Path(workspaces[slot['run_id']]['workspace']).resolve(strict=True)
            if workspace.parent != block or workspace.stat().st_uid != 1000:
                raise ValueError('Workspace must be an independently staged subject-owned directory')
            validate_pilot_admission(reg,slot['arm'],slot['run_id'],workspace)
            for name, expected in workspaces[slot['run_id']]['files_sha256'].items():
                if sha(workspace/name) != expected:
                    raise ValueError('Unlaunched workspace differs from prepared baseline/overlay')
            if (workspace/'node_modules').is_symlink() or not (workspace/'node_modules').is_dir():
                raise ValueError('Independent writable dependencies required')
            if sha(protected(prompts['parent_files_by_run'][slot['run_id']])) != prompts['parent_sha256_by_run'][slot['run_id']]:
                raise ValueError('Parent prompt binding mismatch')
        # Preparation workspaces belong to UID1000 for the subjects; the root-owned
        # staging records above, not subject directory ownership, protect provenance.
        ledger = block/'study-ledger.sqlite'
        Store.initialize(ledger)
        state = {'kind':'registered_C1_calibration_collection','started':stamp(),'registration_sha256':sha(registration_path),
                 'order':admission['order'],'status':'running','runs':[], 'scored_runs':0,
                 'policy':'One dispatch per frozen slot; no model feedback, retries, quality rescue or task selection.'}
        state_path = block/'collection.json'
        def save():
            temp = block/'collection.json.tmp'
            temp.write_text(json.dumps(state,indent=2)+'\n');temp.replace(state_path)
        save()
        for slot in admission['order']:
            subprocess.run([sys.executable,str(REPO/'scripts/preparation_admission.py'),'--private-root',str(PRIVATE),
                            '--cohort-id',block.parent.name],check=True,capture_output=True)
            run_id = slot['run_id']; root = block/('run-'+run_id);root.mkdir(mode=0o700)
            prompt = protected(prompts['parent_files_by_run'][run_id]).read_text()
            row = {**slot,'controller_started':stamp(),'status':'setting_up','root':str(root)}
            state['runs'].append(row);save()
            done = threading.Event()
            def checkpoints():
                next_at = 1800
                while not done.wait(5):
                    try:
                        db = sqlite3.connect(ledger.as_uri()+'?mode=ro',uri=True)
                        try:
                            found = db.execute("SELECT body FROM events WHERE run=? ORDER BY seq",(run_id,)).fetchall()
                        finally:
                            db.close()
                        events = [json.loads(x[0]) for x in found]
                        started = next((x for x in events if x.get('kind')=='dispatch'),None)
                        if started is None:
                            continue
                        elapsed = (time.monotonic_ns()-started['monotonic_ns'])/1e9
                        if elapsed >= next_at:
                            (root/('passive-checkpoint-'+str(next_at)+'.json')).write_text(json.dumps({
                                'observed':stamp(),'elapsed_seconds':elapsed,'event_count':len(events),
                                'kind':'passive_no_model_call_no_response_inspection'},indent=2)+'\n')
                            next_at = 3600 if next_at == 1800 else next_at+3600
                    except Exception as exc:
                        (root/'passive-observer-error.json').write_text(json.dumps({'observed':stamp(),'error_type':type(exc).__name__})+'\n')
            observer = threading.Thread(target=checkpoints,daemon=True);observer.start()
            try:
                report = run_mechanical_workflow(root=root,registration=reg,arm=slot['arm'],prompt=prompt,image=IMAGE,
                    cpus='2,3',workspace=Path(workspaces[run_id]['workspace']),docs=context['docs'],context_inputs=context,
                    gateway_python='/opt/hermes/litellm-1.103.3/venv/bin/python',
                    provider_key_file='/run/credentials/hermes-litellm.service/OPENROUTER_API_KEY',ledger=ledger,
                    phase='calibration',run_id=run_id,public_checks=public_checks)
                row.update(status='first_endpoint_frozen_ungraded',ended=stamp(),endpoint_reason=report['result']['reason'],
                           native_exit_code=report['result']['native']['exit_code'])
                save()
                if report['global_admission_stopped'] or row['endpoint_reason'] not in ('final','deadline'):
                    state.update(status='stopped_preserving_state',ended=stamp());save();return
            except BaseException as exc:
                row.update(status='infrastructure_failure_preserved',ended=stamp(),error_type=type(exc).__name__,error=str(exc))
                state.update(status='stopped_preserving_state',ended=stamp());save();raise
            finally:
                done.set();observer.join(timeout=6)
        state.update(status='ten_first_endpoints_frozen_ungraded',ended=stamp());save()


if __name__ == '__main__':
    main()
