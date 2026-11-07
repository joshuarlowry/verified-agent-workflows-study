"""Real network=none container/Unix-gateway test with a synthetic upstream.

No model calls, benchmark tasks or application acceptance checks are involved.
"""
import hashlib
import http.server
import importlib.util
import json
from pathlib import Path
import secrets
import subprocess
import tempfile
import threading
import time

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('unix_proxy', ROOT/'harness/unix_inference_proxy.py')
proxy=importlib.util.module_from_spec(spec);spec.loader.exec_module(proxy)
requests=[]
key='synthetic-preflight-key-not-a-provider-credential'
class Upstream(http.server.BaseHTTPRequestHandler):
    def log_message(self,*_):pass
    def do_POST(self):
        body=json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        assert self.headers.get('Authorization')=='Bearer '+key
        requests.append(body)
        if body.get('messages',[{}])[0].get('content')=='budget':
            self.send_response(402);self.end_headers();self.wfile.write(b'{"error":"insufficient credits"}');return
        self.send_response(200);self.send_header('Content-Type','text/event-stream');self.end_headers()
        self.wfile.write(b'data: {"id":"synthetic","choices":[{"delta":{"content":"TRANSPORT_ONLY"}}]}\n\n')
        self.wfile.flush()
        self.wfile.write(b'data: {"id":"synthetic","usage":{"prompt_tokens":2,"completion_tokens":1,"cost":0}}\n\ndata: [DONE]\n\n')
        self.wfile.flush()

with tempfile.TemporaryDirectory(prefix='study2-transport-') as temp:
    temp=Path(temp);socket_path=temp/'inference.sock';log=temp/'usage.jsonl'
    upstream=http.server.ThreadingHTTPServer(('127.0.0.1',0),Upstream)
    threading.Thread(target=upstream.serve_forever,daemon=True).start()
    gateway=proxy.UnixServer(str(socket_path),proxy.make_handler('synthetic-alias',f'http://127.0.0.1:{upstream.server_port}',key,log))
    threading.Thread(target=gateway.serve_forever,daemon=True).start()
    name='study2-transport-'+secrets.token_hex(4)
    try:
        cmd=['sudo','-n','podman','run','--detach','--name',name,'--network','none','--memory','8g','--memory-swap','8g','--cpuset-cpus','0,1','--pids-limit','256','--cap-drop','ALL','--security-opt','no-new-privileges','--user','1000:1000','-v',f'{socket_path}:/run/study/inference.sock:ro','-v',f'{ROOT}/harness/container_http_bridge.mjs:/tools/bridge.mjs:ro','docker.io/library/node:24.19.0-bookworm-slim','node','/tools/bridge.mjs','--socket','/run/study/inference.sock']
        subprocess.run(cmd,capture_output=True,text=True,check=True)
        time.sleep(.5)
        program=r'''
const fs=require('fs'),os=require('os');
(async()=>{
 const send=async(body)=>{const r=await fetch('http://127.0.0.1:4000/v1/chat/completions',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(body)});return {status:r.status,body:await r.text()};};
 const good=await send({model:'synthetic-alias',messages:[{role:'user',content:'test'}],stream:true});
 const denied=await send({model:'other-model',messages:[],stream:true});
 const override=await send({model:'synthetic-alias',provider:{only:['other-provider']},messages:[]});
 const budget=await send({model:'synthetic-alias',messages:[{role:'user',content:'budget'}]});
 console.log(JSON.stringify({good,denied,override,budget,externalInterfaces:Object.keys(os.networkInterfaces()).filter(x=>x!=='lo'),hostHomeVisible:fs.existsSync('/home/josh/Documents')}));
})();
'''
        output=subprocess.run(['sudo','-n','podman','exec',name,'node','-e',program],capture_output=True,text=True,check=True)
        result=json.loads(output.stdout);rows=[json.loads(x) for x in log.read_text().splitlines()]
        checks={'stream_roundtrip':result['good']['status']==200 and 'TRANSPORT_ONLY' in result['good']['body'] and '[DONE]' in result['good']['body'],'wrong_model_rejected':result['denied']['status']==403,'route_override_rejected':result['override']['status']==403,'budget_refusal_preserved':result['budget']['status']==402 and json.loads(result['budget']['body'])['error']['budget_exhausted'],'raw_usage_captured':any(x['event']=='usage' and x['usage']['completion_tokens']==1 for x in rows),'network_isolation':not result['externalInterfaces'],'host_paths_absent':not result['hostHomeVisible'],'only_allowed_requests_forwarded':len(requests)==2,'budget_event_logged':any(x['event']=='upstream_rejection' and x['budget_exhausted'] for x in rows)}
        report={'kind':'synthetic_mechanical_transport_not_model_evaluation','checks':checks,'all_passed':all(checks.values()),'model_calls':0,'upstream_calls':len(requests),'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'harness/container_http_bridge.mjs',ROOT/'harness/unix_inference_proxy.py']},'not_yet_qualified':['real OpenCode in container','actual pinned models through socket bridge','Context corpus','Gemma worker broker','full application/evaluator isolation']}
        (ROOT/'setup/transport-preliminary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
        if not report['all_passed']:raise SystemExit(1)
    finally:
        subprocess.run(['sudo','-n','podman','rm','-f',name],capture_output=True)
        gateway.shutdown();gateway.server_close();upstream.shutdown()
