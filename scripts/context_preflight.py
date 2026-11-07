"""Offline Context MCP in a restricted container; existing generic docs only.

This tests mechanics, not the new application's approved documentation corpus.
"""
import datetime
import json
from pathlib import Path
import selectors
import shutil
import secrets
import subprocess
import tempfile
import time

ROOT=Path(__file__).resolve().parents[1]
MODULES=Path('/home/josh/.local/share/neuledge-context/1.3.3/lib/node_modules')
GENERIC=Path('/home/josh/.context/packages/ecmascript-number@2025.db')
with tempfile.TemporaryDirectory(prefix='study2-context-') as temp:
    packages=Path(temp)/'packages';packages.mkdir();shutil.copy2(GENERIC,packages/GENERIC.name)
    name='study2-context-'+secrets.token_hex(4)
    command=['sudo','-n','podman','run','--rm','--name',name,'-i','--network','none','--user','1000:1000','--memory','8g','--memory-swap','8g','--cpuset-cpus','0,1','--pids-limit','256','--cap-drop','ALL','--security-opt','no-new-privileges','-v',f'{MODULES}:/opt/context/node_modules:ro','-v',f'{packages}:/home/node/.context/packages:ro','docker.io/library/node:24.19.0-bookworm-slim','node','/opt/context/node_modules/@neuledge/context/dist/cli.js','serve','--libs','ecmascript-number@2025']
    started=time.monotonic();p=subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);select=selectors.DefaultSelector();select.register(p.stdout,selectors.EVENT_READ)
    def send(value):p.stdin.write(json.dumps(value)+'\n');p.stdin.flush()
    def call(i,method,params):
        send({'jsonrpc':'2.0','id':i,'method':method,'params':params});end=time.monotonic()+20
        while time.monotonic()<end:
            if not select.select(max(0,end-time.monotonic())):break
            line=p.stdout.readline()
            if not line:break
            try:r=json.loads(line)
            except ValueError:continue
            if r.get('id')==i:return r
        raise RuntimeError('No MCP response within mechanical probe timeout')
    result={'kind':'offline_generic_context_mechanical_probe_not_application_corpus_qualification','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'model_calls':0,'server_version_candidate':'1.3.3','exposed_library':'ecmascript-number@2025','network':'none','corpus_mount':'read_only'}
    try:
        init=call(1,'initialize',{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'study2-offline-context','version':'1'}});send({'jsonrpc':'2.0','method':'notifications/initialized'})
        catalog=call(2,'tools/list',{});tools=catalog.get('result',{}).get('tools',[])
        docs=call(3,'tools/call',{'name':'get_docs','arguments':{'library':'ecmascript-number@2025','topic':'Number'}})
        bad=call(4,'tools/call',{'name':'get_docs','arguments':{'library':'unlisted-library@0','topic':'Number'}})
        content=docs.get('result',{}).get('content',[]);texts=[x.get('text','') for x in content if x.get('type')=='text']
        parsed=[json.loads(x) for x in texts]
        relevant=any(x.get('library')=='ecmascript-number@2025' and bool(x.get('results')) for x in parsed)
        result['server']=init.get('result',{}).get('serverInfo');result['tools']=[x['name'] for x in tools]
        result['checks']={'initialize':bool(init.get('result')),'only_scoped_docs_tool':result['tools']==['get_docs'],'retrieval':relevant and not docs.get('result',{}).get('isError',False),'unlisted_library_rejected':bool(bad.get('error') or bad.get('result',{}).get('isError'))}
        result['retrieved_characters']=sum(map(len,texts));result['all_passed']=all(result['checks'].values())
    except Exception as error:result.update(all_passed=False,error_type=type(error).__name__,error=str(error))
    finally:
        cleanup=subprocess.run(['sudo','-n','podman','rm','-f','-t','0',name],capture_output=True,text=True,timeout=20)
        try:p.wait(timeout=5)
        except subprocess.TimeoutExpired:p.kill();p.wait()
        if p.stdin:p.stdin.close();p.stdin=None
        _,stderr=p.communicate(timeout=5)
        result['cleanup_exit_code']=cleanup.returncode
        result['stderr_tail']=stderr[-1500:]
        result['elapsed_seconds_including_cleanup']=time.monotonic()-started
        result['all_passed']=result.get('all_passed',False) and cleanup.returncode==0
    result['still_required']=['actual app-version corpus/source review','exact source/archive hashes and extraction coverage','all role/session adapters and worker inheritance','full study isolation and event capture']
    (ROOT/'setup/context-preliminary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
    if not result['all_passed']:raise SystemExit(1)
