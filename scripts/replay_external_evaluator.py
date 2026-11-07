"""Diagnostic replay: target and frozen evaluator share only an isolated network.

This provisions no model and authors no acceptance assertions. It records the
frozen evaluator's own report/exit without treating this plumbing run as task
qualification. Run from the authorized root preparation controller.
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
import time

IMAGE = '3005436d2c76060957f7944203f2edb281a1ffb33f16e8a85cc68444dfb5ef38'
PRIVATE = Path('/home/josh/.local/state/study2-setup')
REPO = Path(__file__).resolve().parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frozen_copy(source, manifest, target):
    source = source.resolve()
    if not source.is_relative_to(PRIVATE):
        raise ValueError('Only explicitly frozen private preparation sources supported')
    entries = json.loads(manifest.read_text())['files_sha256']
    if not entries:
        raise ValueError('Empty inventory')
    target.mkdir()
    for name, expected in entries.items():
        src = source / name
        if src.is_symlink() or not src.resolve().is_relative_to(source) or not src.is_file():
            raise ValueError('Nonregular/escaping source path')
        if digest(src) != expected:
            raise ValueError('Frozen source mismatch: ' + name)
        dst = target / name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return entries


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--target', required=True, type=Path)
    p.add_argument('--target-inventory', required=True, type=Path)
    p.add_argument('--evaluator', required=True, type=Path)
    p.add_argument('--evaluator-inventory', required=True, type=Path)
    p.add_argument('--suite', choices=['public', 'sealed', 'all'], default='all')
    a = p.parse_args()
    if os.geteuid() != 0:
        raise SystemExit('Requires authorized preparation controller')
    profile_record = json.loads((REPO/'harness/security/profile-source.json').read_text())
    profile = profile_record['profile_name']
    if profile != 'study2-agent-a5ccdae8-stack1':
        raise ValueError('Unregistered profile')
    start = time.monotonic()
    job = PRIVATE / 'external-evaluator-replays' / ('replay-' + secrets.token_hex(6))
    job.mkdir(parents=True, mode=0o700)
    report = {'kind': 'external_evaluator_plumbing_diagnostic_not_task_acceptance',
              'dispatch_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'image_id': IMAGE, 'model_calls': 0, 'commands': [], 'task_qualified': False,
              'controller_sha256': digest(Path(__file__)), 'apparmor_profile': profile}
    names = []
    def command(argv, *, require_zero=True, timeout=600):
        at = time.monotonic()
        index = len(report['commands']) + 1
        try:
            done = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
            stdout, stderr, code = done.stdout, done.stderr, done.returncode
        except subprocess.TimeoutExpired as exc:
            stdout = exc.stdout.decode(errors='replace') if isinstance(exc.stdout, bytes) else exc.stdout or ''
            stderr = exc.stderr.decode(errors='replace') if isinstance(exc.stderr, bytes) else exc.stderr or ''
            code = None
        (job / f'command-{index}.stdout.log').write_text(stdout)
        (job / f'command-{index}.stderr.log').write_text(stderr)
        report['commands'].append({'argv': argv, 'exit_code': code, 'elapsed_seconds': time.monotonic()-at,
                                  'stdout_sha256': hashlib.sha256(stdout.encode()).hexdigest(),
                                  'stderr_sha256': hashlib.sha256(stderr.encode()).hexdigest()})
        if code is None or (require_zero and code != 0):
            raise RuntimeError('Mechanical command failed; see private command ' + str(index))
        return code, stdout
    def exec_in(name, *args, **kwargs):
        return command(['podman', 'exec', name, *args], **kwargs)
    try:
        target = job / 'target'
        checker = job / 'evaluator'
        app_inventory = frozen_copy(a.target, a.target_inventory, target)
        eval_inventory = frozen_copy(a.evaluator, a.evaluator_inventory, checker)
        report['target_inventory_sha256'] = digest(a.target_inventory)
        report['evaluator_inventory_sha256'] = digest(a.evaluator_inventory)
        # Only the evaluator's trusted, pinned Playwright dependencies are needed.
        app_lock = json.loads((target/'package-lock.json').read_text())['packages']
        eval_lock = json.loads((checker/'package-lock.json').read_text())['packages']
        expected = {'node_modules/playwright', 'node_modules/playwright-core'}
        required = {k for k, v in eval_lock.items() if k and not v.get('optional')}
        if required != expected:
            raise ValueError('Evaluator dependencies need a separately qualified offline image')
        for key in expected:
            for field in ['version', 'integrity']:
                if not eval_lock[key].get(field) or eval_lock[key][field] != app_lock[key].get(field):
                    raise ValueError('Trusted image/evaluator dependency mismatch')
        report['evaluator_dependency_source'] = 'Independent writable copy of exact version/integrity-matched Playwright packages from trusted dependency image; never candidate node_modules.'
        state = job/'state'; state.mkdir()
        app_state = state/'app'; eval_state = state/'evaluator'; results = job/'results'
        for directory in [app_state, eval_state, results]: directory.mkdir()
        (checker/'node_modules').mkdir()
        (checker/'browsers').symlink_to('/opt/playwright-browsers')
        for root in [target, checker, state, results]:
            for path in [root, *root.rglob('*')]:
                os.lchown(path, 1000, 1000)
        app_name = 'study2-target-' + secrets.token_hex(5)
        eval_name = 'study2-evaluator-' + secrets.token_hex(5)
        common = ['--detach', '--init', '--read-only', '--tmpfs', '/tmp:rw,nosuid,nodev,size=1g',
                  '--memory', '8g', '--memory-swap', '8g', '--cpuset-cpus', '2,3', '--pids-limit', '256',
                  '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges', '--security-opt', 'apparmor='+profile,
                  '--user', '1000:1000', '-e', 'HOME=/state', '-e', 'npm_config_cache=/state/npm-cache']
        names.append(app_name)
        _, app_id = command(['podman', 'run', '--name', app_name, '--network', 'none', *common,
                  '-e', 'PORT=4010', '-e', 'BETTER_AUTH_URL=http://127.0.0.1:4010',
                  '-e', 'WORKBOARD_DB=external-replay.sqlite',
                  '-v', f'{target}:/target:rw', '-v', f'{app_state}:/state:rw', '--workdir', '/target', IMAGE,
                  'node', '-e', 'setInterval(()=>{},10000)'])
        exec_in(app_name, 'cp', '-R', '/opt/application-deps/node_modules', '/target/node_modules')
        for argv in [['npm', 'run', 'build'], ['npm', 'run', 'reset']]: exec_in(app_name, *argv)
        names.append(eval_name)
        _, eval_id = command(['podman', 'run', '--name', eval_name, '--network', 'container:'+app_name, *common,
                  '-v', f'{checker}:/evaluator:ro', '-v', f'{checker / "node_modules"}:/evaluator/node_modules:rw',
                  '-v', f'{eval_state}:/state:rw', '-v', f'{results}:/results:rw', '--workdir', '/evaluator', IMAGE,
                  'node', '-e', 'setInterval(()=>{},10000)'])
        for package in ['playwright', 'playwright-core']:
            exec_in(eval_name, 'cp', '-R', '/opt/application-deps/node_modules/'+package, '/evaluator/node_modules/'+package)
        probe = "const fs=require('fs');console.log(JSON.stringify({targetVisible:fs.existsSync('/target/server'),node:process.version,playwright:require('playwright/package.json').version,nodeEnv:process.env.NODE_ENV??null,testEnv:process.env.TEST??null}));if(fs.existsSync('/target/server'))process.exit(1)"
        _, visibility = exec_in(eval_name, 'node', '-e', probe)
        report['evaluator_visibility_probe'] = json.loads(visibility)
        report['isolation'] = {'target_container_id': app_id.strip(), 'evaluator_container_id': eval_id.strip(),
                              'network': 'Fresh target network namespace with no external interface; evaluator joins exact target namespace.',
                              'target_mounts': ['/target', '/state'], 'evaluator_mounts': ['/evaluator:ro', '/evaluator/node_modules:rw', '/state', '/results'],
                              'resource_policy': 'Two CPUs/eight GiB separately for this post-endpoint diagnostic; not supervisor/worker aggregate qualification.'}
        command(['podman', 'exec', '--detach', app_name, 'sh', '-c', 'exec npm start > /state/server.stdout.log 2> /state/server.stderr.log'])
        readiness = "import time,urllib.request,sys\nend=time.monotonic()+30\nwhile time.monotonic()<end:\n try:\n  urllib.request.urlopen('http://127.0.0.1:4010/api/health',timeout=1).close();sys.exit(0)\n except Exception:time.sleep(.2)\nsys.exit(1)"
        exec_in(eval_name, 'python3', '-c', readiness, timeout=40)
        code, _ = exec_in(eval_name, 'node', 'bin/c1-eval.mjs', 'check', '--base-url', 'http://127.0.0.1:4010',
                          '--suite', a.suite, '--json-out', '/results/evaluator-report.json', require_zero=False)
        report['evaluator_exit_code'] = code
        output = results/'evaluator-report.json'
        if not output.is_file() or not isinstance(json.loads(output.read_text()), dict):
            raise RuntimeError('Evaluator did not retain a JSON object report')
        report['evaluator_report_sha256'] = digest(output)
        report['target_source_unchanged'] = all(digest(target/name)==sha for name,sha in app_inventory.items())
        report['evaluator_source_unchanged'] = all(digest(checker/name)==sha for name,sha in eval_inventory.items())
        report['plumbing_completed'] = report['target_source_unchanged'] and report['evaluator_source_unchanged']
        report['scope'] = 'Report/exit retained verbatim; known checker findings and later repairs remain separate. This diagnostic is not positive/negative/task acceptance or full isolation qualification.'
    except BaseException as exc:
        report.update(plumbing_completed=False, error_type=type(exc).__name__, error=str(exc))
    finally:
        report['cleanup'] = []
        for name in reversed(names):
            try:
                code, _ = command(['podman', 'rm', '-f', '-t', '0', name], require_zero=False, timeout=30)
                report['cleanup'].append({'container': name, 'exit_code': code})
            except Exception as exc:
                report['cleanup'].append({'container': name, 'error_type': type(exc).__name__})
        report['elapsed_seconds_including_cleanup'] = time.monotonic()-start
        report['ended_at_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        (job/'controller.json').write_text(json.dumps(report, indent=2)+'\n')
        print(json.dumps({'receipt': str(job/'controller.json'), 'plumbing_completed': report.get('plumbing_completed',False),
                          'evaluator_exit_code': report.get('evaluator_exit_code'), 'task_qualified': False}))
    if not report.get('plumbing_completed') or any(x.get('exit_code')!=0 for x in report['cleanup']):
        raise SystemExit(1)


if __name__ == '__main__':
    main()
