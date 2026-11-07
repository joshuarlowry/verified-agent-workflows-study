"""Generic container enforcement/CPU-contention probe; not app qualification."""
import concurrent.futures
import datetime
import json
import statistics
import subprocess
from pathlib import Path

IMAGE='docker.io/library/node:24.19.0-bookworm-slim'
PROGRAM=r'''
const fs=require('fs'),os=require('os'),{Worker}=require('worker_threads');
const started=performance.now();
const job=`require('crypto').pbkdf2Sync('study2-generic','fixed-salt',1000000,32,'sha256')`;
Promise.all([0,1].map(()=>new Promise((ok,no)=>{const w=new Worker(job,{eval:true});w.on('error',no);w.on('exit',x=>x?no(new Error('worker exit '+x)):ok());}))).then(()=>console.log(JSON.stringify({seconds:(performance.now()-started)/1000,node:process.version,cpus:os.availableParallelism(),cpuset:fs.readFileSync('/sys/fs/cgroup/cpuset.cpus.effective','utf8').trim(),memoryMax:fs.readFileSync('/sys/fs/cgroup/memory.max','utf8').trim(),memoryEvents:fs.readFileSync('/sys/fs/cgroup/memory.events','utf8'),hostHomeVisible:fs.existsSync('/home/josh/Documents'),externalInterfaces:Object.keys(os.networkInterfaces()).filter(x=>x!=='lo')})));
'''

def one(lane):
    cpus='0,1' if lane==0 else '2,3'
    cmd=['sudo','-n','podman','run','--rm','--network','none','--memory','8g','--memory-swap','8g','--cpuset-cpus',cpus,'--pids-limit','256','--cap-drop','ALL','--security-opt','no-new-privileges',IMAGE,'node','-e',PROGRAM]
    p=subprocess.run(cmd,capture_output=True,text=True,check=True)
    return {'lane':lane,**json.loads(p.stdout)}

if __name__=='__main__':
    result={'kind':'generic_preliminary_not_full_application_lane_qualification','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'trials_per_mode_lane':5,'image':IMAGE,'solo':[],'parallel':[]}
    for lane in [0,1]:
        for _ in range(5):result['solo'].append(one(lane))
    for _ in range(5):
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:result['parallel'].extend(pool.map(one,[0,1]))
    result['median_inflation_by_lane']={str(lane):statistics.median(x['seconds'] for x in result['parallel'] if x['lane']==lane)/statistics.median(x['seconds'] for x in result['solo'] if x['lane']==lane)-1 for lane in [0,1]}
    result['generic_resource_checks_passed']=all(x['cpus']==2 and x['memoryMax']=='8589934592' and not x['hostHomeVisible'] and not x['externalInterfaces'] for mode in ['solo','parallel'] for x in result[mode])
    result['generic_contention_threshold_passed']=all(v<=.10 for v in result['median_inflation_by_lane'].values())
    result['unqualified']=['actual app install/build/typecheck/Playwright replay','inference rate limits','complete subject mounts/network/inference broker','background preparation workload may affect this preliminary result']
    dest=Path(__file__).resolve().parents[1]/'setup/resource-preliminary.json';dest.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ['solo','parallel']}))
