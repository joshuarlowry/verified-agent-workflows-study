"""Publish only allowlisted workflow metadata; never read subject responses.

The queue invokes this at dispatch and every endpoint. Git publication failure
is recorded locally and does not turn an unqualified construction into success.
"""
import argparse
import datetime
import json
import os
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PRIVATE = Path('/home/josh/.local/state/study2-setup')
MODELS = {'google/gemma-4-31b-it', 'z-ai/glm-5.3-flash', 'openai/gpt-6.1-terra'}
STATES = {'queued', 'running', 'returned_requires_cross_review', 'blocked_preserved'}
FILES = ['setup/launch.json', 'setup/status.json', 'setup/RUN_STATUS.md']

def snapshot(manifest, service):
    rows = []
    for role in manifest['roles']:
        if role['model'] not in MODELS or role['status'] not in STATES:
            raise ValueError('Unregistered model or role state')
        if not re.fullmatch(r'[a-zA-Z0-9_-]+', role['role']):
            raise ValueError('Invalid role identifier')
        rows.append({k: role[k] for k in ('role', 'run_id', 'model', 'status', 'dispatch_utc', 'ended_at_utc', 'agent_exit_code', 'controller_exit_code', 'api_budget_exhausted', 'prompt_sha256', 'controller_sha256') if k in role})
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    return {**{k: manifest[k] for k in ('retry_of', 'original_failure_preserved', 'retry_policy') if k in manifest}, 'launch_id': manifest['launch_id'], 'kind': 'preparation_construction_not_calibration_or_scoring', 'snapshot_at_utc': now, 'status': manifest['status'], 'background_service': service, 'automatic_restart': False, 'roles': rows, 'qualification_status': 'not_qualified', 'notification': 'This repository status is updated automatically at dispatch and endpoints. No chat/push/email notification is configured.', 'scope': 'Current construction jobs only; successful return still requires cross-review and qualification. No calibration or scored dispatch authorized by this queue.'}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--service', required=True)
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    manifest_path = args.manifest.resolve()
    if not manifest_path.is_relative_to(PRIVATE.resolve()) or manifest_path.name != 'manifest.json':
        raise ValueError('Manifest must be a private preparation manifest')
    if not re.fullmatch(r'study2-[a-z0-9-]+(?:\.service)?', args.service):
        raise ValueError('Invalid study service identifier')
    data = snapshot(json.loads(manifest_path.read_text()), args.service)
    if args.dry_run:
        print(json.dumps(data, indent=2)); return
    status_path = ROOT/'setup/status.json'
    status = json.loads(status_path.read_text())
    status.update(updated_at_utc=data['snapshot_at_utc'], status='preparation_'+data['status'], active_launch='setup/launch.json', launch_snapshot_note='See automatically updated setup/RUN_STATUS.md; successful construction returns are unqualified.')
    lines = ['# Current run status', '', 'Updated: '+data['snapshot_at_utc'], '', '**'+data['status'].replace('_', ' ')+'**', '', '| Job | Model | State |', '|---|---|---|']
    lines += [f"| {r['role']} | {r['model']} | {r['status'].replace('_', ' ')} |" for r in data['roles']]
    lines += ['', 'A returned job is not yet reviewed or qualified. A blocked job needs diagnosis; its original endpoint is preserved. This queue cannot start calibration or scored runs.', '', 'This page updates automatically at job transitions. It is not a live heartbeat. No chat/push/email notification is configured. [Machine-readable status](launch.json).', '']
    for path, text in [(ROOT/FILES[0], json.dumps(data,indent=2)+'\n'), (status_path, json.dumps(status,indent=2)+'\n'), (ROOT/FILES[2], '\n'.join(lines))]:
        path.write_text(text)
        if os.geteuid() == 0: os.chown(path,1000,1000)
    if args.publish:
        prefix = ['/usr/sbin/runuser','-u','josh','--'] if os.geteuid()==0 else []
        def git(*argv):
            return subprocess.run(prefix+['git','-C',str(ROOT),*argv], check=True, capture_output=True, text=True)
        # Refuse to include unrelated staged material in an automatic commit.
        staged = set(git('diff','--cached','--name-only').stdout.splitlines())
        if staged-set(FILES): raise RuntimeError('Unrelated staged files; refusing automatic commit')
        git('add','--',*FILES)
        if git('diff','--cached','--name-only').stdout.strip():
            git('commit','-m','Update preparation workflow status')
        git('push','origin','HEAD')
    print('Preparation status saved'+(' and pushed' if args.publish else ''))

if __name__ == '__main__': main()
