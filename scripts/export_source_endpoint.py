"""Mechanically commit an unchanged source-only first return against frozen baseline.

This supplies Git packaging only, never repairs application/test bytes. Original
source and model endpoint remain untouched. A second clean clone must reproduce
all returned file hashes by applying the generated application-only patch.
"""
import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess

BASELINE = 'ac96364336be35f0d8d7dadb2717b951cd3c9ac4'
PRIVATE = Path('/home/josh/.local/state/study2-setup')

def inventory(root):
    files = {}
    for p in root.rglob('*'):
        if '.git' in p.relative_to(root).parts:
            continue
        s = p.lstat()
        if stat.S_ISLNK(s.st_mode) or (not stat.S_ISDIR(s.st_mode) and not stat.S_ISREG(s.st_mode)):
            raise ValueError('Only source files/directories are accepted')
        if p.is_file():
            files[p.relative_to(root).as_posix()] = {
                'sha256': hashlib.sha256(p.read_bytes()).hexdigest(),
                'executable': bool(s.st_mode & 0o111),
            }
    if not files:
        raise ValueError('Empty source')
    return files

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True, type=Path)
    parser.add_argument('--baseline', required=True, type=Path)
    parser.add_argument('--destination', required=True, type=Path)
    parser.add_argument('--branch', default='fixture/c1-gemma-alternative-repair')
    parser.add_argument('--application-author', default='google/gemma-4-31b-it')
    parser.add_argument('--commit-message', default='Package Gemma C1 repair first-return source unchanged')
    args = parser.parse_args()
    if os.geteuid() != 0:
        raise ValueError('Use the root preparation controller')
    source = args.source.resolve(strict=True)
    baseline = args.baseline.resolve(strict=True)
    destination = args.destination.resolve()
    if not all(p.is_relative_to(PRIVATE) for p in (source, baseline, destination)):
        raise ValueError('Private study source/destination required')
    if destination.exists() or destination.is_relative_to(source) or destination.is_relative_to(baseline):
        raise ValueError('Use a new destination outside source trees')
    before = inventory(source)
    env = {'PATH': '/usr/bin:/bin', 'LANG': 'C.UTF-8', 'GIT_CONFIG_NOSYSTEM': '1',
           'GIT_CONFIG_GLOBAL': '/dev/null', 'GIT_TERMINAL_PROMPT': '0',
           'GIT_AUTHOR_NAME': 'Study mechanical controller', 'GIT_AUTHOR_EMAIL': 'study-controller@localhost',
           'GIT_COMMITTER_NAME': 'Study mechanical controller', 'GIT_COMMITTER_EMAIL': 'study-controller@localhost'}
    def git(path, *argv):
        return subprocess.run(['/usr/bin/git', '-c', 'core.hooksPath=/dev/null', '-c', 'safe.directory='+str(path), '-C', str(path), *argv],
                              env=env, capture_output=True, check=True).stdout
    if git(baseline, 'rev-parse', 'HEAD').decode().strip() != BASELINE:
        raise ValueError('Wrong baseline commit')
    git(baseline, 'check-ref-format', '--branch', args.branch)
    destination.mkdir(mode=0o700)
    repo = destination/'source'
    git(destination, 'clone', '--no-local', '--no-hardlinks', str(baseline), str(repo))
    git(repo, 'checkout', '-b', args.branch)
    for p in repo.iterdir():
        if p.name == '.git':
            continue
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
    for name in before:
        target = repo/name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source/name, target)
    if inventory(repo) != before:
        raise ValueError('Source copy mismatch')
    git(repo, 'add', '--all')
    git(repo, 'commit', '--allow-empty', '-m', args.commit_message)
    commit = git(repo, 'rev-parse', 'HEAD').decode().strip()
    patch = destination/'baseline.patch'
    patch.write_bytes(git(repo, 'diff', '--binary', BASELINE, commit, '--', '.'))
    replay = destination/'roundtrip'
    git(destination, 'clone', '--no-local', '--no-hardlinks', str(baseline), str(replay))
    if patch.stat().st_size:
        git(replay, 'apply', '--check', str(patch))
        git(replay, 'apply', str(patch))
    if inventory(replay) != before or inventory(source) != before:
        raise ValueError('Patch roundtrip or untouched-source verification failed')
    bundle = destination/'endpoint.bundle'
    git(repo, 'bundle', 'create', str(bundle), '--all')
    record = {'kind': 'mechanical_source_endpoint_packaging_not_implementation_or_acceptance',
              'recorded_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'application_author': args.application_author,
              'branch': args.branch,
              'commit_author': 'Study mechanical controller', 'original_model_source_unchanged': True,
              'baseline_commit': BASELINE, 'packaged_commit': commit,
              'application_tree': git(repo, 'rev-parse', 'HEAD^{tree}').decode().strip(),
              'patch_sha256': hashlib.sha256(patch.read_bytes()).hexdigest(),
              'bundle_sha256': hashlib.sha256(bundle.read_bytes()).hexdigest(),
              'files': before, 'patch_roundtrip_exact': True,
              'qualification': 'No model authorship/commit claim, source review or acceptance implied.'}
    (destination/'receipt.json').write_text(json.dumps(record, indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if k != 'files'}))

if __name__ == '__main__':
    main()
