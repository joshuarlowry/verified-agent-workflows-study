"""Build a local preparation image; never dispatch agents or change production.

Image ID and package manifest freeze the result; apt repositories are moving,
so the Containerfile alone is not claimed to be a reproducible image snapshot.
"""
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
ROOT=Path(__file__).resolve().parents[1]
reg=json.loads((ROOT/'registration.json').read_text())
source=ROOT/reg['application_preparation']['current_candidate_path']/'baseline'
modules=Path('/home/josh/.local/share/neuledge-context/1.3.3/lib/node_modules')
cli=Path('/home/josh/.opencode/bin/opencode')
inputs={'application_lock_sha256':hashlib.sha256((source/'package-lock.json').read_bytes()).hexdigest(),'application_package_sha256':hashlib.sha256((source/'package.json').read_bytes()).hexdigest(),'containerfile_sha256':hashlib.sha256((ROOT/'harness/Study.Containerfile').read_bytes()).hexdigest(),'opencode_binary_sha256':hashlib.sha256(cli.read_bytes()).hexdigest()}
module_rows=[]
for p in sorted(modules.rglob('*')):
    if p.is_symlink():
        if not p.resolve().is_relative_to(modules.resolve()):raise ValueError('Context dependency symlink escapes frozen modules')
        module_rows.append([str(p.relative_to(modules)),'symlink',str(p.readlink())])
    elif p.is_file():module_rows.append([str(p.relative_to(modules)),hashlib.sha256(p.read_bytes()).hexdigest()])
inputs['context_modules_tree_sha256']=hashlib.sha256(json.dumps(module_rows,separators=(',',':')).encode()).hexdigest()
identity=hashlib.sha256(json.dumps(inputs,sort_keys=True).encode()).hexdigest()
tag='localhost/study2-preparation:'+identity[:16]
private=Path('/home/josh/.local/state/study2-setup/image-builds');private.mkdir(exist_ok=True)
record=private/identity
record.mkdir()  # never overwrite an earlier image build endpoint
start=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
with tempfile.TemporaryDirectory(prefix='study2-image-') as temp:
    temp=Path(temp)
    for name,file in [('application-package.json',source/'package.json'),('application-package-lock.json',source/'package-lock.json'),('Containerfile',ROOT/'harness/Study.Containerfile'),('opencode',cli)]:shutil.copy2(file,temp/name)
    shutil.copytree(modules,temp/'context-modules',symlinks=True)
    with (record/'build.log').open('w') as log:
        process=subprocess.run(['sudo','-n','podman','build','--tag',tag,'--file',str(temp/'Containerfile'),str(temp)],stdout=log,stderr=subprocess.STDOUT)
report={'kind':'local_preparation_dependency_image_not_execution_qualification','dispatch_utc':utc,'elapsed_seconds':time.monotonic()-start,'exit_code':process.returncode,'model_calls':0,'input_hashes':inputs,'tag':tag,'image_id':None,'limitations':['moving apt repositories; retain final image ID/package manifest rather than claiming source-only reproducibility','no application source, corpus archives, broker or acceptance evaluator in image','full clean-instance app and containment checks remain pending']}
if process.returncode==0:
    report['image_id']=json.loads(subprocess.check_output(['sudo','-n','podman','image','inspect',tag]))[0]['Id']
    command="node --version && npm --version && opencode --version && git --version && rg --version && python3 --version && sqlite3 --version && dpkg-query -W"
    probe=subprocess.run(['sudo','-n','podman','run','--rm','--init','--network','none','--cap-drop','ALL','--security-opt','no-new-privileges',tag,'sh','-c',command],capture_output=True,text=True)
    report['version_manifest_exit_code']=probe.returncode
    (record/'package-versions.txt').write_text(probe.stdout)
    report['version_manifest_sha256']=hashlib.sha256(probe.stdout.encode()).hexdigest()
    (ROOT/'setup/image-package-versions.txt').write_text(probe.stdout)
(record/'controller.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'setup/image-build-preliminary.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
if process.returncode:raise SystemExit(process.returncode)
