"""Zero-model shared-budget/separate-network/freeze probe for two-role workflows.

Tests actual pod/cgroup boundaries, including detached descendants, rather than
claiming Unix process groups are a complete endpoint boundary.
"""
import datetime,json,secrets,subprocess,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
image=json.loads((ROOT/'setup/image-build-preliminary.json').read_text())['image_id']
profile=json.loads((ROOT/'harness/security/profile-source.json').read_text())['profile_name']
name='study2-pod-boundary-'+secrets.token_hex(5);start=time.monotonic();utc=datetime.datetime.now(datetime.timezone.utc).isoformat();group=None;frozen=False
program=r'''
const fs=require('fs'),http=require('http'),os=require('os'),{spawn}=require('child_process');const role=process.argv[1];
let appWrite='ok';try{fs.writeFileSync('/app/'+role+'.proof',role)}catch(e){appWrite=e.code}
const child=spawn(process.execPath,['-e',"const fs=require('fs');setInterval(()=>fs.appendFileSync('/state/detached.ticks','x'),10)"],{detached:true,stdio:'ignore'});child.unref();
setInterval(()=>fs.appendFileSync('/state/main.ticks','x'),10);
const status=fs.readFileSync('/proc/self/status','utf8');http.createServer((q,r)=>r.end(JSON.stringify({role,appWrite,parallelism:os.availableParallelism(),externalInterfaces:Object.keys(os.networkInterfaces()).filter(x=>x!=='lo'),capEff:status.match(/^CapEff:\s*(.*)$/m)?.[1],noNewPrivs:status.match(/^NoNewPrivs:\s*(.*)$/m)?.[1],seccomp:status.match(/^Seccomp:\s*(.*)$/m)?.[1],hostWorkspace:fs.existsSync('/home/josh/Documents')}))).listen(4000,'127.0.0.1');
'''
def run(args,**kwargs):return subprocess.run(['sudo','-n','podman',*args],capture_output=True,text=True,check=True,**kwargs)
def read(path):return subprocess.check_output(['sudo','-n','cat',str(path)],text=True).strip()
def write(path,value):subprocess.run(['sudo','-n','tee',str(path)],input=value,text=True,capture_output=True,check=True)
with tempfile.TemporaryDirectory(prefix='study2-pod-boundary-') as temp:
    temp=Path(temp);app=temp/'app';app.mkdir(mode=0o777)
    try:
        run(['pod','create','--name',name,'--share=none','--infra=false','--cpuset-cpus','0,1','--memory','8g','--memory-swap','8g'])
        for role in ['parent','worker']:
            state=temp/role;state.mkdir(mode=0o777)
            run(['run','--detach','--init','--name',name+'-'+role,'--pod',name,'--network','none','--http-proxy=false','--read-only','--tmpfs','/tmp:rw,nosuid,nodev,size=128m','--cap-drop','ALL','--security-opt','no-new-privileges','--security-opt','apparmor='+profile,'--user','1000:1000','-v',f'{state}:/state:rw','-v',f'{app}:/app:'+('ro' if role=='parent' else 'rw'),image,'node','-e',program,role])
        info=json.loads(run(['pod','inspect',name]).stdout);info=info[0] if isinstance(info,list) else info
        group=Path('/sys/fs/cgroup')/info['CgroupPath']
        if group.parent.parent!=Path('/sys/fs/cgroup') or info['Id'] not in group.name:raise ValueError('Unexpected controller-owned pod cgroup path')
        write(group/'pids.max','512')
        time.sleep(.25);actors={}
        for role in ['parent','worker']:
            actors[role]=json.loads(run(['exec',name+'-'+role,'node','-e',"fetch('http://127.0.0.1:4000').then(async r=>console.log(await r.text()))"]).stdout)
        limits={field:read(group/field) for field in ['memory.max','memory.swap.max','cpuset.cpus.effective','pids.max']}
        write(group/'cgroup.freeze','1');frozen=True
        until=time.monotonic()+3
        while 'frozen 1' not in read(group/'cgroup.events'):
            if time.monotonic()>until:raise RuntimeError('No trusted group freeze acknowledgement')
            time.sleep(.02)
        paths=[temp/role/file for role in ['parent','worker'] for file in ['main.ticks','detached.ticks']]
        before=[p.read_bytes() for p in paths];time.sleep(.2);unchanged=all(p.read_bytes()==old and len(old)>0 for p,old in zip(paths,before))
        write(group/'cgroup.freeze','0');frozen=False;time.sleep(.2);resumed=all(len(p.read_bytes())>len(old) for p,old in zip(paths,before))
        checks={'separate_loopback_namespaces':actors['parent']['role']=='parent' and actors['worker']['role']=='worker','aggregate_memory_swap_cpu_pids':limits=={'memory.max':'8589934592','memory.swap.max':'0','cpuset.cpus.effective':'0-1','pids.max':'512'},'supervisor_app_readonly_worker_writable':actors['parent']['appWrite']=='EROFS' and actors['worker']['appWrite']=='ok' and (app/'worker.proof').read_text()=='worker' and not (app/'parent.proof').exists(),'zero_caps_nnp_seccomp_no_egress_host_paths':all(a['capEff']=='0000000000000000' and a['noNewPrivs']=='1' and a['seccomp']=='2' and not a['externalInterfaces'] and not a['hostWorkspace'] for a in actors.values()),'freeze_stops_both_roles_and_detached_descendants':unchanged,'unfreeze_positive_control_resumes_all_writers':resumed}
        report={'kind':'mechanical_actual_pod_boundary_not_model_or_endpoint_controller_qualification','model_calls':0,'dispatch_utc':utc,'image_id':image,'profile':profile,'actors':actors,'aggregate_limits':limits,'checks':checks,'all_passed':all(checks.values()),'qualification_limits':['native-final/deadline/controller integration not tested','actual inference/Context/broker not tested','not full two-lane performance qualification']}
    finally:
        if frozen and group:write(group/'cgroup.freeze','0')
        run(['pod','rm','-f',name])
    report['elapsed_seconds_including_cleanup']=time.monotonic()-start
    (ROOT/'setup/pod-boundary-preliminary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
    if not report['all_passed']:raise SystemExit(1)
