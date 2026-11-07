"""Zero-model-call isolation of the container child-signal failure.

Unconfined variants are diagnostic controls only, never subject treatments.
The study candidate keeps default seccomp, zero capabilities and NNP, and uses
its own AppArmor profile; existing host/runtime profiles are unchanged.
"""
import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import time
ROOT=Path(__file__).resolve().parents[1]
image=json.loads((ROOT/'setup/image-build-preliminary.json').read_text())['image_id']
profile=json.loads((ROOT/'harness/security/profile-source.json').read_text())
program=r'''
const {spawn}=require('child_process'),fs=require('fs'),os=require('os');
const status=fs.readFileSync('/proc/self/status','utf8');
const c=spawn('sleep',['1'],{stdio:'ignore'});let error=null,ok=false;
setTimeout(()=>{try{process.kill(c.pid,'SIGTERM');ok=true}catch(e){error=e.code}},100);
c.on('exit',(code,signal)=>console.log(JSON.stringify({killSucceeded:ok,error,childExitCode:code,childExitSignal:signal,uid:process.getuid(),capEff:status.match(/^CapEff:\s*(.*)$/m)?.[1],noNewPrivs:status.match(/^NoNewPrivs:\s*(.*)$/m)?.[1],seccomp:status.match(/^Seccomp:\s*(.*)$/m)?.[1],externalInterfaces:Object.keys(os.networkInterfaces()).filter(x=>x!=='lo')})));
'''
variants=[('runtime_default',[]),('add_KILL_diagnostic',['--cap-add','KILL']),('unconfined_seccomp_diagnostic',['--security-opt','seccomp=unconfined']),('unconfined_apparmor_diagnostic',['--security-opt','apparmor=unconfined']),('study_scoped_profile',['--security-opt','apparmor='+profile['profile_name']])]
rows=[]
for name,extra in variants:
    start=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat()
    result=subprocess.run(['sudo','-n','podman','run','--rm','--init','--network','none','--http-proxy=false','--cap-drop','ALL','--security-opt','no-new-privileges',*extra,'--user','1000:1000','--entrypoint','node',image,'-e',program],capture_output=True,text=True,timeout=15)
    row={'variant':name,'dispatch_utc':utc,'elapsed_seconds':time.monotonic()-start,'exit_code':result.returncode,'result':json.loads(result.stdout) if result.returncode==0 else None,'stderr':result.stderr}
    rows.append(row)
by={r['variant']:r for r in rows}
checks={'default_failure_reproduced':not by['runtime_default']['result']['killSucceeded'],'KILL_not_a_fix':not by['add_KILL_diagnostic']['result']['killSucceeded'],'seccomp_not_a_fix':not by['unconfined_seccomp_diagnostic']['result']['killSucceeded'],'apparmor_control_succeeds':by['unconfined_apparmor_diagnostic']['result']['killSucceeded'],'scoped_profile_succeeds':by['study_scoped_profile']['result']['killSucceeded'],'candidate_retains_zero_caps_nnp_seccomp_and_network_none':by['study_scoped_profile']['result']['capEff']=='0000000000000000' and by['study_scoped_profile']['result']['noNewPrivs']=='1' and by['study_scoped_profile']['result']['seccomp']=='2' and not by['study_scoped_profile']['result']['externalInterfaces']}
report={'kind':'mechanical_container_signal_diagnosis_not_model_evaluation','model_calls':0,'image_id':image,'profile_sha256':hashlib.sha256((ROOT/'harness/security/study2-agent.profile').read_bytes()).hexdigest(),'variants':rows,'checks':checks,'all_passed':all(checks.values()),'qualification_limits':['profile source requires different-model review','not full role/isolation/endpoint-race qualification']}
(ROOT/'setup/signal-preliminary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if not report['all_passed']:raise SystemExit(1)
