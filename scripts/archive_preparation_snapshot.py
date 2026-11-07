"""Private, incremental preparation snapshots with complete inventories.

Prior archives remain immutable. A new archive carries changed/new sanitized
files and a parent digest; its manifest lists the entire current snapshot.
This is a passive checkpoint, not an atomic endpoint or a credential backup.
"""
import argparse
import datetime
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import tarfile

EXCLUDE={'agent-home','node_modules','.cache','dist','.tmp','.git','test-results','playwright-report','__pycache__','home','browsers','playwright-browsers','ms-playwright'}
MANIFEST='CHECKPOINT_MANIFEST.json'

def digest(data):return hashlib.sha256(data).hexdigest()

def safe_relative(name):
    p=PurePosixPath(name)
    if p.is_absolute() or not p.parts or any(x in ('..','.') for x in p.parts):
        raise ValueError('Unsafe archive path')
    return p

def archive_manifest(path):
    with tarfile.open(path,'r|gz') as tar:
        found=None
        for member in tar:
            if member.name==MANIFEST:
                if found is not None or not member.isfile():raise ValueError('Invalid snapshot manifest')
                found=json.load(tar.extractfile(member))
        if found is None:raise ValueError('Snapshot manifest missing')
    return found

def add_bytes(tar,name,data,mtime=0):
    safe_relative(name)
    info=tarfile.TarInfo(name);info.size=len(data);info.mode=0o600;info.mtime=mtime
    tar.addfile(info,io.BytesIO(data))

def snapshot(root,dest,secret_values=(),parent=None):
    root=Path(root).resolve();dest=Path(dest).resolve()
    if dest.is_relative_to(root):raise ValueError('Backup destination must be outside source')
    (dest/'checkpoints').mkdir(parents=True,exist_ok=True)
    previous={}
    if parent is not None:
        path=materialize_archive(dest,parent['archive'],parent['sha256'])
        previous={r['path']:r for r in archive_manifest(path)['files']}
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    target=dest/'checkpoints'/('preparation-'+stamp+'.tar.gz')
    secrets=[x for x in secret_values if x]
    rows=[];redactions=0;changed=0;unavailable=[]
    with tarfile.open(target,'x:gz') as tar:
        for base,dirs,files in os.walk(root):
            dirs[:]=sorted(d for d in dirs if d not in EXCLUDE and not d.startswith(('chromium-','chromium_headless_shell-','ffmpeg-')))
            for name in sorted(files):
                p=Path(base)/name;rel=p.relative_to(root);relative=rel.as_posix()
                if p.is_symlink() or name.endswith('.key') or name.startswith('.env') or name.endswith('.tsbuildinfo') or relative=='backup_preparation.py':continue
                if relative==MANIFEST:raise ValueError('Reserved snapshot manifest name exists in source')
                if p.suffix in ['.db','.sqlite','.sqlite3'] and not any('corpus' in part or part=='context-packages' for part in rel.parts):continue
                try:data=p.read_bytes();mtime=p.stat().st_mtime
                except OSError as error:
                    unavailable.append({'path':relative,'errno':error.errno});continue
                original=digest(data);count=0
                for key in secrets:
                    if key in data:
                        if b'\0' in data:raise ValueError('Credential in binary; refuse export')
                        count+=data.count(key);data=data.replace(key,b'<REDACTED_CREDENTIAL>')
                assert not any(key in data for key in secrets)
                exported=digest(data)
                if previous.get(relative,{}).get('export_sha256')!=exported:
                    add_bytes(tar,relative,data,mtime);changed+=1
                rows.append({'path':relative,'original_sha256':original,'export_sha256':exported,'bytes':len(data),'known_credential_redactions':count});redactions+=count
        manifest={'format_version':2,'archive_type':'incremental' if parent else 'full','parent':parent,'captured_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'private passive preparation checkpoint; active files can be partial; not an atomic endpoint','credential_policy':'Known provider and per-run gateway credentials redacted; key/env files and agent private homes excluded; restore does not recover credentials.','excluded':'Dependency/browser/build caches, disposable test databases, credentials and agent homes. Official raw source archives and supported corpus database paths are retained.','known_credential_redactions':redactions,'changed_files_in_this_archive':changed,'unavailable_during_capture':unavailable,'files':rows,'restore':'Resolve this archive and its verified parent chain; restore only paths in this complete manifest, verifying each export_sha256. Never blindly overlay obsolete paths from old archives.'}
        add_bytes(tar,MANIFEST,json.dumps(manifest,indent=2).encode())
    summary={'archive':str(target.relative_to(dest)),'sha256':digest(target.read_bytes()),'bytes':target.stat().st_size,'files':len(rows),'changed_files':changed,'format_version':2,'parent':parent,'known_credential_redactions':redactions,'unavailable_files':len(unavailable),'captured_at_utc':manifest['captured_at_utc'],'scope':manifest['scope']}
    sidecar=target.with_name(target.stem+'.json');sidecar.write_text(json.dumps(summary,indent=2)+'\n')
    return summary

def latest_tracked_parent(dest):
    # A local committed parent will be pushed with descendants if a prior push
    # failed. Untracked/passively incomplete archives never become parents.
    prefix=['/usr/sbin/runuser','-u','josh','--'] if os.geteuid()==0 else []
    result=subprocess.run(prefix+['git','-C',str(dest),'ls-files','--','checkpoints/*.tar.json'],check=True,capture_output=True,text=True)
    candidates=[]
    for name in result.stdout.splitlines():
        p=dest/name;d=json.loads(p.read_text())
        if d.get('archive') and d.get('sha256'):candidates.append(d)
    if not candidates:return None
    d=max(candidates,key=lambda x:x['captured_at_utc'])
    return {'archive':d['archive'],'sha256':d['sha256']}

def materialize_archive(dest,relative,expected_sha):
    relative=str(safe_relative(relative));path=dest/relative
    if path.exists():
        if digest(path.read_bytes())!=expected_sha:raise ValueError('Archive digest mismatch')
        return path
    parts_file=path.with_name(path.name+'.parts.json')
    parts=json.loads(parts_file.read_text())
    if parts['original_archive_sha256']!=expected_sha:raise ValueError('Parts manifest digest disagrees with archive summary')
    cache=dest/'.restore-cache';cache.mkdir(exist_ok=True)
    output=cache/path.name
    if not output.exists():
        temp=output.with_name(output.name+'.partial')
        try:
            with temp.open('xb') as out:
                for row in parts['parts']:
                    part=dest/safe_relative(row['path']);data=part.read_bytes()
                    if len(data)!=row['bytes'] or digest(data)!=row['sha256']:raise ValueError('Archive part corruption')
                    out.write(data)
            if digest(temp.read_bytes())!=expected_sha:raise ValueError('Reassembled archive corruption')
            temp.rename(output)
        except BaseException:
            temp.unlink(missing_ok=True);raise
    if digest(output.read_bytes())!=expected_sha:raise ValueError('Cached archive corruption')
    return output

def restore(dest,latest,target):
    """Restore sanitized files from a locally available archive chain."""
    dest=Path(dest).resolve();target=Path(target).resolve()
    if target.exists():raise ValueError('Restore target must not exist')
    latest=Path(latest)
    if latest.is_absolute():latest=latest.relative_to(dest)
    summary_path=dest/latest
    summary=json.loads(summary_path.with_name(summary_path.stem+'.json').read_text())
    if summary['archive']!=str(latest):raise ValueError('Latest summary identity mismatch')
    latest=materialize_archive(dest,str(latest),summary['sha256'])
    manifest=archive_manifest(latest);remaining={r['path']:r for r in manifest['files']}
    if len(remaining)!=len(manifest['files']):raise ValueError('Duplicate manifest paths')
    for name in remaining:safe_relative(name)
    target.mkdir(parents=True);restored=set();seen=set();path=latest
    while True:
        resolved=path.resolve()
        if not resolved.is_relative_to(dest) or resolved in seen:raise ValueError('Unsafe/cyclic parent chain')
        seen.add(resolved);current=None;members=set()
        with tarfile.open(path,'r|gz') as tar:
            for member in tar:
                if member.name in members:raise ValueError('Duplicate archive member')
                members.add(member.name);safe_relative(member.name)
                if not member.isfile():raise ValueError('Non-file archive member')
                if member.name==MANIFEST:current=json.load(tar.extractfile(member));continue
                if member.name not in remaining:continue
                row=remaining[member.name];data=tar.extractfile(member).read()
                if digest(data)!=row['export_sha256'] or len(data)!=row['bytes']:raise ValueError('Restored content does not match inventory')
                output=target/safe_relative(member.name);output.parent.mkdir(parents=True,exist_ok=True)
                with output.open('xb') as file:file.write(data)
                os.chmod(output,0o600);restored.add(member.name);del remaining[member.name]
        if current is None:raise ValueError('Parent manifest missing')
        if not remaining:break
        parent=current.get('parent')
        if not parent:raise ValueError('Incomplete snapshot chain')
        path=materialize_archive(dest,parent['archive'],parent['sha256'])
    return {'files_restored':len(restored),'archives_read':len(seen),'sanitized':True}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',type=Path);p.add_argument('--destination',required=True,type=Path)
    p.add_argument('--secret-file',action='append',default=[],type=Path)
    p.add_argument('--restore-archive',type=Path);p.add_argument('--target',type=Path)
    args=p.parse_args()
    if args.restore_archive:
        if not args.target or args.root:p.error('Restore requires --target and no --root')
        print(json.dumps(restore(args.destination,args.restore_archive,args.target)));return
    if not args.root:p.error('Snapshot requires --root')
    secrets=[x.read_bytes().strip() for x in args.secret_file]+[x.read_bytes().strip() for x in args.root.glob('*/probe.key')]
    parent=latest_tracked_parent(args.destination)
    row=snapshot(args.root,args.destination,secrets,parent)
    if os.geteuid()==0:
        for path in [args.destination/'checkpoints',args.destination/row['archive'],(args.destination/row['archive']).with_name(Path(row['archive']).stem+'.json')]:os.chown(path,1000,1000)
    print(json.dumps(row))

if __name__=='__main__':main()
