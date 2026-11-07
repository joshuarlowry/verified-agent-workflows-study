"""Exercise archive restoration, corruption rejection and credential redaction."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tarfile
import tempfile
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('snapshot',ROOT/'scripts/archive_preparation_snapshot.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
checks={}
with tempfile.TemporaryDirectory() as tmp:
 b=Path(tmp);src=b/'src';src.mkdir();dest=b/'dest'
 for name,content in {'source.py':'v1','removed.txt':'old','config.json':'{"key":"synthetic-secret-value"}','probe.key':'synthetic-secret-value'}.items():(src/name).write_text(content)
 (src/'official.tgz').write_bytes(b'official-source-archive')
 first=m.snapshot(src,dest,[b'synthetic-secret-value']);(src/'source.py').write_text('v2');(src/'removed.txt').unlink();(src/'new.txt').write_text('new')
 second=m.snapshot(src,dest,[b'synthetic-secret-value'],{k:first[k] for k in ['archive','sha256']})
 checks['only_changed_files_written']=second['changed_files']==2
 out=b/'restored';r=m.restore(dest,second['archive'],out)
 checks['chain_restores_current_bytes']=(out/'source.py').read_text()=='v2' and (out/'new.txt').read_text()=='new' and r['archives_read']==2
 checks['removed_path_not_restored']=not (out/'removed.txt').exists()
 checks['credential_redacted_key_file_excluded']='synthetic-secret-value' not in (out/'config.json').read_text() and not (out/'probe.key').exists()
 checks['official_archive_retained']=(out/'official.tgz').read_bytes()==b'official-source-archive'
 before=(dest/first['archive']).read_bytes();third=m.snapshot(src,dest,[b'synthetic-secret-value'],{k:second[k] for k in ['archive','sha256']})
 checks['unchanged_snapshot_has_no_bodies']=third['changed_files']==0
 checks['old_archives_immutable']=(dest/first['archive']).read_bytes()==before
 old=dest/first['archive'];old.write_bytes(before+b'corruption')
 try:m.restore(dest,second['archive'],b/'corrupt-restore');checks['corrupt_parent_rejected']=False
 except ValueError:checks['corrupt_parent_rejected']=True
 try:m.safe_relative('../escape');checks['unsafe_paths_rejected']=False
 except ValueError:checks['unsafe_paths_rejected']=True
 (src/'binary.bin').write_bytes(b'\0synthetic-secret-value')
 try:m.snapshot(src,dest,[b'synthetic-secret-value']);checks['binary_credential_export_rejected']=False
 except ValueError:checks['binary_credential_export_rejected']=True
with tempfile.TemporaryDirectory() as tmp:
 b=Path(tmp);src=b/'src';src.mkdir();dest=b/'dest';(src/'a').write_text('first');one=m.snapshot(src,dest)
 (src/'a').write_text('second');two=m.snapshot(src,dest,parent={k:one[k] for k in ['archive','sha256']})
 p=dest/one['archive'];data=p.read_bytes();part=p.with_name(p.name+'.part000');part.write_bytes(data)
 p.with_name(p.name+'.parts.json').write_text(json.dumps({'original_archive_sha256':one['sha256'],'parts':[{'path':str(part.relative_to(dest)),'bytes':len(data),'sha256':one['sha256']}]}));p.unlink()
 checks['split_archive_restores_without_original_tar']=m.restore(dest,one['archive'],b/'restored')['files_restored']==1 and (b/'restored/a').read_text()=='first'
 q=dest/two['archive'];q.write_bytes(q.read_bytes()+b'corruption')
 try:m.restore(dest,two['archive'],b/'bad');checks['latest_archive_corruption_rejected']=False
 except ValueError:checks['latest_archive_corruption_rejected']=True
with tempfile.TemporaryDirectory() as tmp:
 b=Path(tmp);dest=b/'dest';(dest/'checkpoints').mkdir(parents=True);path=dest/'checkpoints/old.tar.gz';data=b'legacy';row={'path':'old.txt','export_sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
 with tarfile.open(path,'w:gz') as tar:
  m.add_bytes(tar,'old.txt',data);m.add_bytes(tar,m.MANIFEST,json.dumps({'files':[row]}).encode())
 summary={'archive':'checkpoints/old.tar.gz','sha256':hashlib.sha256(path.read_bytes()).hexdigest()};(dest/'checkpoints/old.tar.json').write_text(json.dumps(summary))
 checks['legacy_full_archive_compatible']=m.restore(dest,summary['archive'],b/'out')['files_restored']==1 and (b/'out/old.txt').read_bytes()==data
report={'kind':'synthetic_snapshot_restore_and_redaction_checks_not_model_calls','checks':checks,'all_passed':all(checks.values()),'model_calls':0,'source_sha256':hashlib.sha256((ROOT/'scripts/archive_preparation_snapshot.py').read_bytes()).hexdigest(),'test_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(ROOT/'setup/incremental-backup-checks.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'all_passed':report['all_passed'],'checks':len(checks)}))
if not report['all_passed']:raise SystemExit(1)
