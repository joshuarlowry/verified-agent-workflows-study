"""Back up private preparation at a batch endpoint, without exposing contents."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

REPO = Path('/home/josh/Documents/Model Mechanisms/verified-agent-workflows-artifacts')
HELPER = '/home/josh/.local/state/study2-setup/backup_preparation.py'

def main():
    result = subprocess.run(['/usr/bin/python3', HELPER], check=True, capture_output=True, text=True)
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

if __name__=='__main__':main()
