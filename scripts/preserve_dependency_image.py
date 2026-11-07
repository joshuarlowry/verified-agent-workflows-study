"""Preserve the exact preparation image as a private release asset, not a rollout."""
import datetime
import gzip
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import time

IMAGE = '3005436d2c76060957f7944203f2edb281a1ffb33f16e8a85cc68444dfb5ef38'
REPOSITORY = 'joshuarlowry/verified-agent-workflows-artifacts'
ROOT = Path('/home/josh/.local/state/study2-image-preservation')


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as src:
        for chunk in iter(lambda: src.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    if os.geteuid() != 0:
        raise SystemExit('Requires the authorized preparation controller identity')
    ROOT.mkdir(exist_ok=True, mode=0o700)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    job = ROOT / stamp
    job.mkdir(mode=0o700)
    started = time.monotonic()
    receipt = {'created_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'image_id': IMAGE, 'kind': 'dependency_image_preservation_not_study_qualification',
               'repository': REPOSITORY, 'model_calls': 0, 'published_private': False}
    def save():
        (job / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    def run(args, **kwargs):
        p = subprocess.run(args, capture_output=True, text=True, **kwargs)
        if p.returncode:
            raise RuntimeError('Command failed: ' + args[0] + ' exit ' + str(p.returncode))
        return p.stdout.strip()
    gh = ['/usr/sbin/runuser', '-u', 'josh', '--', 'gh']
    try:
        visibility = json.loads(run(gh + ['repo', 'view', REPOSITORY, '--json', 'visibility']))
        if visibility['visibility'] != 'PRIVATE':
            raise RuntimeError('Artifact repository is not private')
        actual = run(['podman', 'image', 'inspect', IMAGE, '--format', '{{.Id}}'])
        if actual.removeprefix('sha256:') != IMAGE:
            raise RuntimeError('Source image mismatch')
        # Scan the actual uncompressed image root, not compressed archive bytes.
        private = Path('/home/josh/.local/state/study2-setup')
        keys = [Path('/run/credentials/hermes-litellm.service/OPENROUTER_API_KEY').read_bytes().strip()]
        keys += [p.read_bytes().strip() for p in private.glob('*/probe.key')]
        keys = [k for k in keys if k]
        mount = Path(run(['podman', 'image', 'mount', IMAGE]))
        scanned = 0
        try:
            overlap = max(map(len, keys)) - 1
            for directory, _, names in os.walk(mount, followlinks=False):
                for name in names:
                    path = Path(directory) / name
                    if not stat.S_ISREG(path.lstat().st_mode):
                        continue
                    tail = b''
                    with path.open('rb') as src:
                        for chunk in iter(lambda: src.read(1024 * 1024), b''):
                            data = tail + chunk
                            if any(k in data for k in keys):
                                raise RuntimeError('Known credential found in image; upload denied')
                            tail = data[-overlap:] if overlap else b''
                    scanned += 1
        finally:
            run(['podman', 'image', 'unmount', IMAGE])
        receipt['known_credential_scan'] = {'files': scanned, 'matches': 0,
            'scope': 'Known provider and preparation gateway credential bytes only; not a general secrets certification'}
        archive = job / 'study2-dependencies.oci.tar'
        run(['podman', 'save', '--format', 'oci-archive', '--output', str(archive), IMAGE])
        receipt['oci_archive'] = {'sha256': sha(archive), 'bytes': archive.stat().st_size}
        # Load into independent storage so existing source layers cannot mask a bad archive.
        storage = job / 'restore-storage'
        runtime = job / 'restore-runtime'
        podman = ['podman', '--root', str(storage), '--runroot', str(runtime), '--storage-driver', 'vfs']
        run(podman + ['load', '--input', str(archive)])
        restored = run(podman + ['image', 'inspect', IMAGE, '--format', '{{.Id}}'])
        if restored.removeprefix('sha256:') != IMAGE:
            raise RuntimeError('Independent-storage restore image mismatch')
        receipt['independent_storage_restore'] = {'image_id': restored, 'passed': True}
        shutil.rmtree(storage)
        shutil.rmtree(runtime, ignore_errors=True)
        compressed = archive.with_suffix('.tar.gz')
        with archive.open('rb') as src, gzip.open(compressed, 'wb', compresslevel=1) as dst:
            shutil.copyfileobj(src, dst, length=1024 * 1024)
        receipt['compressed_archive'] = {'sha256': sha(compressed), 'bytes': compressed.stat().st_size}
        assets = []
        if compressed.stat().st_size > 1800 * 1024 * 1024:
            with compressed.open('rb') as src:
                index = 0
                while chunk := src.read(512 * 1024 * 1024):
                    part = job / (compressed.name + f'.part{index:03}')
                    part.write_bytes(chunk)
                    assets.append(part)
                    index += 1
        else:
            assets.append(compressed)
        receipt['assets'] = [{'name': p.name, 'sha256': sha(p), 'bytes': p.stat().st_size} for p in assets]
        receipt['restore_instructions'] = 'Download assets; verify listed SHA256. Concatenate listed parts in order if split, gunzip to OCI tar, verify OCI SHA256, podman load -i TAR, verify image ID.'
        receipt['release_tag'] = 'dependency-image-' + IMAGE[:12]
        receipt['elapsed_seconds_before_upload'] = time.monotonic() - started
        save()
        # Publication directory is private to the host user, outside subject mounts and checkpoints.
        os.chown(job, 1000, 1000)
        os.chmod(job, 0o700)
        for path in assets + [job / 'receipt.json']:
            os.chown(path, 1000, 1000)
            os.chmod(path, 0o600)
        notes = job / 'RELEASE_NOTES.md'
        notes.write_text('Exact preparation dependency image. Private recovery artifact; not a benchmark result or launch qualification.\n\nImage ID: `' + IMAGE + '`. See receipt.json for hashes, independent-storage restore evidence and restoration instructions. No application source, task solutions or corpus is part of the image.\n')
        os.chown(notes, 1000, 1000)
        run(gh + ['release', 'create', receipt['release_tag'], '--repo', REPOSITORY,
                  '--prerelease', '--title', 'Study 2 dependency image ' + IMAGE[:12],
                  '--notes-file', str(notes), *map(str, assets), str(job / 'receipt.json')])
        remote = json.loads(run(gh + ['release', 'view', receipt['release_tag'], '--repo', REPOSITORY, '--json', 'url,assets']))
        by_name = {a['name']: a for a in remote['assets']}
        for expected in receipt['assets']:
            asset = by_name.get(expected['name'])
            if not asset or asset['size'] != expected['bytes']:
                raise RuntimeError('Remote asset missing or wrong size')
        receipt.update(published_private=True, release_url=remote['url'], elapsed_seconds=time.monotonic()-started,
                       remote_verification='Release asset names and sizes; local archive digest and independent-storage restore. No remote download/digest verification yet.')
        save()
        run(gh + ['release', 'upload', receipt['release_tag'], '--repo', REPOSITORY, '--clobber', str(job/'receipt.json')])
        print(json.dumps({'receipt': str(job/'receipt.json'), 'release_url': remote['url'], 'published_private': True}))
    except BaseException as exc:
        receipt.update(failed=True, failure_type=type(exc).__name__, failure=str(exc), elapsed_seconds=time.monotonic()-started)
        save()
        raise


if __name__ == '__main__':
    main()
