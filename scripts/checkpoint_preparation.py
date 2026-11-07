"""Back up private preparation at a batch endpoint, without exposing contents."""
import argparse
import datetime
import hashlib
import fcntl
import json
import os
from pathlib import Path
import subprocess

REPO = Path('/home/josh/Documents/Model Mechanisms/verified-agent-workflows-artifacts')
HELPER = '/home/josh/.local/state/study2-setup/backup_preparation.py'

def main():
    if os.geteuid()!=0:raise SystemExit('Run from the authorized root preparation controller')
    result = subprocess.run(['/usr/bin/python3', HELPER], capture_output=True, text=True)
    if result.returncode:
        private = Path(HELPER).parent
        keys = [Path('/run/credentials/hermes-litellm.service/OPENROUTER_API_KEY').read_text().strip()]
        keys += [p.read_text().strip() for p in private.glob('*/probe.key')]
        stdout, stderr = result.stdout, result.stderr
        for key in keys:
            if key:
                stdout=stdout.replace(key,'<REDACTED_CREDENTIAL>')
                stderr=stderr.replace(key,'<REDACTED_CREDENTIAL>')
        stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        receipt=private/('checkpoint-producer-failure-'+stamp+'.json')
        with receipt.open('x') as out:
            json.dump({'recorded_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'producer_exit_code':result.returncode,'sanitized_stdout':stdout,'sanitized_stderr':stderr,'scope':'Artifact producer failure, not a model/primary endpoint; failed attempt retained and not silently retried.'},out,indent=2)
        raise RuntimeError('Checkpoint producer failed; sanitized diagnostic retained at '+str(receipt))
    row = json.loads(result.stdout.strip().splitlines()[-1])
    archive = (REPO/row['archive']).resolve()
    if not archive.is_relative_to((REPO/'checkpoints').resolve()):
        raise ValueError('Unexpected checkpoint path')
    if hashlib.sha256(archive.read_bytes()).hexdigest() != row['sha256']:
        raise ValueError('Checkpoint digest mismatch')
    sidecar = archive.with_name(archive.stem+'.json')
    files = [sidecar]
    # Keep each Git blob under GitHub's per-file limit. This is artifact
    # transport sizing, not a model spend or token limit.
    if archive.stat().st_size > 90*1024*1024:
        parts = []
        with archive.open('rb') as source:
            index = 0
            while block := source.read(64*1024*1024):
                part = archive.with_name(archive.name+f'.part{index:03}')
                with part.open('xb') as target: target.write(block)
                if os.geteuid()==0: os.chown(part,1000,1000)
                parts.append({'path':str(part.relative_to(REPO)), 'sha256':hashlib.sha256(block).hexdigest(), 'bytes':len(block)})
                files.append(part); index += 1
        split = archive.with_name(archive.name+'.parts.json')
        split.write_text(json.dumps({'original_archive_sha256':row['sha256'],'reassemble':'Concatenate parts in listed order, then verify original digest.','parts':parts},indent=2)+'\n')
        if os.geteuid()==0: os.chown(split,1000,1000)
        files.append(split)
    else: files.append(archive)
    prefix = ['/usr/sbin/runuser','-u','josh','--'] if os.geteuid()==0 else []
    def git(*args):
        return subprocess.run(prefix+['git','-C',str(REPO),*args],check=True,capture_output=True,text=True)
    if git('diff','--cached','--name-only').stdout.strip():
        raise RuntimeError('Unrelated staged files; checkpoint remains local')
    git('add','-f','--',*[str(p.relative_to(REPO)) for p in files])
    git('commit','-m','Preserve preparation batch endpoint and raw audit artifacts')
    git('push','origin','HEAD')
    print(json.dumps({'checkpoint':row['archive'],'sha256':row['sha256'],'bytes':row['bytes'],'published_private':True}))

if __name__=='__main__':
    argparse.ArgumentParser(description=__doc__).parse_args()
    if os.geteuid()!=0:raise SystemExit('Run from the authorized root preparation controller')
    with (REPO/'.git/study-checkpoint.lock').open('a') as lock:
        if os.geteuid()==0:os.chown(lock.name,1000,1000)
        fcntl.flock(lock,fcntl.LOCK_EX)
        main()
