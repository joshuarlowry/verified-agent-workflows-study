"""Deterministic caller for the registered, separately admitted C1 calibration schedule.

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



def validate_schedule(admission, prior=None):
    order = admission.get('order', [])
    if admission.get('admitted') is not True or admission.get('workflows') != len(order) or not 1 <= len(order) <= 10:
        raise ValueError('Registered C1 schedule has not been admitted')
    if len({x['run_id'] for x in order}) != len(order):
        raise ValueError('Repeated execution identity')
    recovery = admission.get('outage_recovery')
    if recovery is None:
        if len(order) != 10:
            raise ValueError('A shortened schedule needs complete outage provenance')
        return
    if not prior or prior['status'] != 'stopped_preserving_state':
        raise ValueError('Recovery requires a preserved terminal collection')
    retained = [x for x in prior['runs'] if x.get('endpoint_reason') in ('final', 'deadline')]
    if recovery['retained_run_ids'] != [x['run_id'] for x in retained]:
        raise ValueError('Every earlier ordinary endpoint must be retained')
    retained_ids = {x['run_id'] for x in retained}
    interrupted = [x for x in prior['runs'] if x['run_id'] not in retained_ids]
    if not interrupted or any(x.get('endpoint_reason') != 'infrastructure_failure' for x in interrupted):
        raise ValueError('Only documented infrastructure interruptions may be replaced')
    remaining = [x for x in prior['order'] if x['run_id'] not in retained_ids]
    if len(retained) + len(order) != 10 or len(order) != len(remaining):
        raise ValueError('Recovery changes the complete ten-slot sample')
    for actual, original in zip(order, remaining):
        if actual.get('prior_run_id') != original['run_id'] or any(actual[k] != original[k] for k in ('position', 'task', 'arm', 'repetition')):
            raise ValueError('Recovery changes arm, task, repetition or relative order')
        if actual['run_id'] in {x['run_id'] for x in prior['order']}:
            raise ValueError('Recovery must use fresh execution identities')



def validate_unrun_resume(state, admission, ledger_rows, stopped):
    if state.get('status') != 'stopped_preserving_state' or stopped:
        raise ValueError('Resume requires a terminal collection without a global stop')
    if state.get('order') != admission['order']:
        raise ValueError('The frozen schedule changed')
    rows = state.get('runs', [])
    if not 0 < len(rows) < len(admission['order']):
        raise ValueError('Resume needs both preserved outcomes and unrun slots')
    expected = [x['run_id'] for x in admission['order'][:len(rows)]]
    if [x['run_id'] for x in rows] != expected:
        raise ValueError('Completed outcomes must be the exact scheduled prefix')
    if set(dict(ledger_rows)) != set(expected):
        raise ValueError('Ledger and preserved outcomes differ')
    for row in rows:
        if row.get('endpoint_reason') not in ('final', 'deadline', 'infrastructure_failure') or row.get('status') != 'first_endpoint_frozen_ungraded':
            raise ValueError('Unsupported or incomplete endpoint; preserve state')
        if dict(ledger_rows)[row['run_id']] != row['endpoint_reason']:
            raise ValueError('Ledger endpoint state differs')
        if row.get('backup_receipt', {}).get('published_private') is not True or row.get('backup_error_type'):
            raise ValueError('Preserved endpoint backup required')
        if row.get('actual_provider_resolution') == 'unverified_or_drift':
            raise ValueError('Unresolved serving drift blocks continuation')
    return admission['order'][len(rows):]


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--registration', required=True, type=Path)
    p.add_argument('--block', required=True, type=Path)
    p.add_argument('--resume-unrun', type=Path, help='Protected admission for unrun slots only; never restart an agent')
    p.add_argument('--validate-only', action='store_true', help='Check local admission without model calls or collection writes')
    a = p.parse_args()
    if os.geteuid() != 0:
        raise SystemExit('Authorized root controller required')
    block = protected(a.block)
    with (block/'collection.lock').open('a') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        registration_path = protected(a.registration)
        reg = json.loads(registration_path.read_text())
        admission = reg['calibration_initial_block']
        prior = None
        if admission.get('outage_recovery'):
            lineage = admission['outage_recovery']
            prior_path = protected(lineage['prior_collection'])
            if sha(prior_path) != lineage['prior_collection_sha256']:
                raise ValueError('Recovery lineage changed')
            prior = json.loads(prior_path.read_text())
        validate_schedule(admission, prior)
        state_path = block/'collection.json'
        pending_slots = admission['order']
        resumed_state = None
        resume_record = None
        if a.resume_unrun is not None:
            subprocess.run([sys.executable,str(REPO/'scripts/preparation_admission.py'),'--private-root',str(PRIVATE),'--cohort-id',block.parent.name],check=True,capture_output=True)
            resume_path = protected(a.resume_unrun)
            resume_record = json.loads(resume_path.read_text())
            if resume_record.get('admitted') is not True or resume_record['caller_sha256'] != sha(Path(__file__)) or resume_record['registration_sha256'] != sha(registration_path):
                raise ValueError('Unrun continuation is not bound to this caller/registration')
            if sha(protected(state_path)) != resume_record['stopped_collection_sha256']:
                raise ValueError('Preserved collection state changed')
            resumed_state = json.loads(state_path.read_text())
            db = sqlite3.connect((block/'study-ledger.sqlite').as_uri()+'?mode=ro',uri=True)
            try:
                pending_slots = validate_unrun_resume(resumed_state, admission, db.execute('SELECT id,state FROM runs').fetchall(), bool(db.execute('SELECT 1 FROM stop').fetchone()))
            finally:
                db.close()
            if [x['run_id'] for x in pending_slots] != resume_record['pending_run_ids']:
                raise ValueError('Unrun continuation changes the remaining schedule')
            for row in resumed_state['runs']:
                for name in ['endpoint.json','endpoint.json.quiescence.json','controller.json','provider-resolution/verification.json']:
                    relative = 'run-'+row['run_id']+'/'+name
                    if sha(protected(block/relative)) != resume_record['preserved_files_sha256'][relative]:
                        raise ValueError('Preserved endpoint evidence changed')
                evidence = block/('run-'+row['run_id'])
                if json.loads((evidence/'provider-resolution/verification.json').read_text())['status'] != 'verified' or json.loads((evidence/'endpoint.json').read_text())['status'] != 'copied_and_empty_unqualified' or json.loads((evidence/'endpoint.json.quiescence.json').read_text()).get('pod_empty_after_quiescence') is not True:
                    raise ValueError('Serving/freeze/quiescence must be verified before continuation')
        elif state_path.exists():
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
        from core import Store, registered_model
        from check_registered_serving import preflight, postflight
        staged = json.loads(protected(block/'prepared-workspaces.json').read_text())
        workspaces = {r['run_id']:r for r in staged['records']}
        docs = manifests['docs']
        context = {key: Path(docs[key]) for key in ['docs','docs_manifest','packages','package_manifest','approval']}
        context['expected_approval_sha256'] = docs['approval_sha256']
        public_checks = protected(manifests['acceptance']['public_checks'])
        prompts = manifests['prompts']
        for slot in pending_slots:
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
        if a.validate_only:
            print(json.dumps({'local_admission_valid':True,'pending_run_ids':[x['run_id'] for x in pending_slots],'preserved_outcomes':len(resumed_state['runs']) if resumed_state else 0,'model_calls':0}))
            return
        ledger = block/'study-ledger.sqlite'
        if resumed_state is None:
            Store.initialize(ledger)
            state = {'kind':'registered_C1_calibration_collection','started':stamp(),'registration_sha256':sha(registration_path),
                     'order':admission['order'],'status':'running','runs':[], 'scored_runs':0,
                     'policy':'One dispatch per frozen slot; no model feedback, retries, quality rescue or task selection.'}
        else:
            state = resumed_state
            state['status'] = 'running'
            previous_ended = state.pop('ended', None)
            state.setdefault('controller_continuations', []).append({'started':stamp(),'previous_collection_ended':previous_ended,'admission_sha256':sha(resume_path),'preserved_collection_sha256':resume_record['stopped_collection_sha256'],'pending_run_ids':[x['run_id'] for x in pending_slots],'policy':'Only unrun frozen slots; all existing outcomes/identities/endpoints remain unchanged.'})
        def save():
            temp = block/'collection.json.tmp'
            temp.write_text(json.dumps(state,indent=2)+'\n');temp.replace(state_path)
        save()
        for slot in pending_slots:
            subprocess.run([sys.executable,str(REPO/'scripts/preparation_admission.py'),'--private-root',str(PRIVATE),
                            '--cohort-id',block.parent.name],check=True,capture_output=True)
            run_id = slot['run_id']; root = block/('run-'+run_id);root.mkdir(mode=0o700)
            prompt = protected(prompts['parent_files_by_run'][run_id]).read_text()
            row = {**slot,'controller_started':stamp(),'status':'setting_up','root':str(root)}
            state['runs'].append(row);save()
            backup_failed = False
            done = threading.Event()
            models_by_role = {role:registered_model(reg,slot['arm'],role) for role in
                             (['supervisor','worker'] if 'supervising' in slot['arm'] else ['complete_agent'])}
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
                preflight(list(models_by_role.values()),block/('provider-preflight-'+run_id))
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
                try:
                    postflight(root,models_by_role,'/run/credentials/hermes-litellm.service/OPENROUTER_API_KEY')
                    row['actual_provider_resolution'] = 'verified';save()
                except Exception as exc:
                    # Administrative postflight cannot change the primary endpoint.
                    row.update(actual_provider_resolution='unverified_or_drift',postflight_error_type=type(exc).__name__)
                    state.update(status='stopped_preserving_state',ended=stamp());save();return
            except BaseException as exc:
                row.update(status='infrastructure_failure_preserved',ended=stamp(),error_type=type(exc).__name__,error=str(exc))
                state.update(status='stopped_preserving_state',ended=stamp());save();raise
            finally:
                done.set();observer.join(timeout=6)
                # Back up only between workflows, so compression/publication never
                # competes with a timed subject. This is the controller ledger,
                # not an application database. Its supported SQLite snapshot is
                # retained explicitly; disposable app databases remain excluded.
                row['backup_started'] = stamp();save()
                try:
                    source = sqlite3.connect(ledger.as_uri()+'?mode=ro',uri=True)
                    destination = sqlite3.connect(root/'controller-ledger.snapshot')
                    try:
                        source.backup(destination)
                        if destination.execute('PRAGMA integrity_check').fetchone() != ('ok',):
                            raise ValueError('Controller ledger backup failed integrity check')
                        (root/'controller-ledger.sql').write_text('\n'.join(destination.iterdump())+'\n')
                    finally:
                        destination.close();source.close()
                    parent_role = 'supervisor' if 'supervising' in slot['arm'] else 'complete_agent'
                    home = root/(parent_role+'-home')
                    native_db = home/'.local/share/opencode/opencode.db'
                    if native_db.exists():
                        # Preserve supported native state after process quiescence;
                        # never follow a subject-created link out of its home.
                        for part in [home,home/'.local',home/'.local/share',native_db.parent,native_db]:
                            if part.is_symlink():
                                raise ValueError('Native-state backup path contains a symlink')
                        if not native_db.is_file() or native_db.stat().st_nlink != 1:
                            raise ValueError('Native-state backup is not a private regular file')
                        native_source = sqlite3.connect(native_db.as_uri()+'?mode=ro',uri=True)
                        native_snapshot = sqlite3.connect(root/'captures/parent/native-state.snapshot')
                        try:
                            native_source.backup(native_snapshot)
                            if native_snapshot.execute('PRAGMA integrity_check').fetchone() != ('ok',):
                                raise ValueError('Native-state snapshot failed integrity check')
                        finally:
                            native_snapshot.close();native_source.close()
                        row['parent_native_state_snapshot'] = 'preserved'
                    else:
                        row['parent_native_state_snapshot'] = 'unavailable'
                    backup = subprocess.run([sys.executable,str(REPO/'scripts/checkpoint_preparation.py')],
                                            capture_output=True,text=True)
                    (root/'checkpoint.stdout.log').write_text(backup.stdout)
                    (root/'checkpoint.stderr.log').write_text(backup.stderr)
                    if backup.returncode:
                        raise ValueError('Private checkpoint publication failed; preserve endpoint and stop admission')
                    row.update(backup_ended=stamp(),backup_receipt=json.loads(backup.stdout.strip().splitlines()[-1]))
                    save()
                except Exception as exc:
                    row.update(backup_ended=stamp(),backup_error_type=type(exc).__name__)
                    state.update(status='stopped_preserving_state',ended=stamp());save();backup_failed=True
            if backup_failed:
                return
        state.update(status='registered_first_endpoints_frozen_ungraded',ended=stamp());save()


if __name__ == '__main__':
    main()
