"""Exercise startup refusal before any API/model call."""
import hashlib,json,os,subprocess,sys,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
patch=HERE/'sitecustomize.py';launcher=HERE/'launch_gateway.py'
digest=hashlib.sha256(patch.read_bytes()).hexdigest()
base={k:v for k,v in os.environ.items() if k in ['PATH','LANG','TZ']}
def check(name,env,sha=digest,path=launcher,code=78):
 r=subprocess.run([sys.executable,str(path),'--patch-sha256',sha,'--verify-only'],env=env,capture_output=True,text=True,timeout=60)
 assert r.returncode==code,(name,r.returncode,r.stderr)
 assert ('"event": "study_gateway_verified"' in r.stderr)==(code==0),(name,r.stderr)
 return name
valid=dict(base,PYTHONPATH=str(HERE),STUDY_LITELLM_DONE_FIX='1')
checks=[check('verified_overlay_allows_startup',valid,code=0),
check('missing_flag_refused',dict(base,PYTHONPATH=str(HERE))),
check('mistyped_flag_refused',dict(base,PYTHONPATH=str(HERE),STUDY_LITELLM_DONE_FIX='true')),
check('missing_overlay_import_refused',dict(base,STUDY_LITELLM_DONE_FIX='1')),
check('changed_patch_refused',valid,sha='0'*64)]
driver="import sys,runpy;sys.modules.pop('sitecustomize',None);sys.argv="+repr([str(launcher),'--patch-sha256',digest,'--verify-only'])+";runpy.run_path("+repr(str(launcher))+",run_name='__main__')"
probe=subprocess.run([sys.executable,'-c',driver],env=valid,capture_output=True,text=True,timeout=60)
assert probe.returncode==78 and 'study_gateway_verified' not in probe.stderr,(probe.returncode,probe.stderr)
checks.append('absent_startup_module_refused_without_self_import')
with tempfile.TemporaryDirectory(prefix='study2-source-guard-') as d:
 directory=Path(d);source=patch.read_text();old=source.split('EXPECTED_SOURCE_SHA256 = "')[1].split('"')[0]
 altered=source.replace(old,'0'*64,1);(directory/'sitecustomize.py').write_text(altered)
 (directory/'launch_gateway.py').write_text(launcher.read_text())
 checks.append(check('changed_upstream_refused',dict(base,PYTHONPATH=d,STUDY_LITELLM_DONE_FIX='1'),sha=hashlib.sha256(altered.encode()).hexdigest(),path=directory/'launch_gateway.py'))
print(json.dumps({'kind':'mechanical_no_model_calls','all_passed':True,'checks':checks,'patch_sha256':digest,'gateway_launcher_sha256':hashlib.sha256(launcher.read_bytes()).hexdigest()},indent=2))
