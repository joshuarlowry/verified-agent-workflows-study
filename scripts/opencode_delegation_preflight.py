"""Synthetic OpenCode tool round trip in the network-disabled lane.

Makes no model calls. This checks CLI/bridge/gateway mechanics only; it does
not qualify actual provider accounting, corpus or the supervised broker.
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

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('unix_proxy', ROOT/'harness/unix_inference_proxy.py')
proxy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proxy)
requests = []
key = 'synthetic-only-not-a-provider-key'
class Upstream(http.server.BaseHTTPRequestHandler):
    def log_message(self, *_): pass
    def do_POST(self):
        payload = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        assert self.headers.get('Authorization') == 'Bearer '+key
        requests.append(payload)
        self.send_response(200)
        self.send_header('Content-Type', 'text/event-stream')
        self.end_headers()
        index = len(requests)
        def emit(delta, finish=None, usage=None):
            data = {'id': f'synthetic-{index}', 'object': 'chat.completion.chunk', 'created': 1, 'model': 'synthetic-alias', 'choices': [{'index': 0, 'delta': delta, 'finish_reason': finish}]}
            if usage: data['usage'] = usage
            self.wfile.write(('data: '+json.dumps(data)+'\n\n').encode())
            self.wfile.flush()
        if index == 1:
            emit({'role': 'assistant', 'tool_calls': [{'index': 0, 'id': 'synthetic-shell-call', 'type': 'function', 'function': {'name': 'subagent', 'arguments': json.dumps({'agent': 'explore', 'description': 'Synthetic forbidden delegation', 'prompt': 'Return SYNTHETIC_CHILD_SHOULD_NOT_RUN'})}}]})
            emit({}, 'tool_calls')
        else:
            emit({'role': 'assistant', 'content': 'SYNTHETIC_ADAPTER_READY'})
            emit({}, 'stop')
        emit({}, usage={'prompt_tokens': 10, 'completion_tokens': 2, 'total_tokens': 12})
        self.wfile.write(b'data: [DONE]\n\n')
        self.wfile.flush()

start = time.monotonic()
with tempfile.TemporaryDirectory(prefix='study2-native-transport-') as temp:
    temp = Path(temp)
    temp.chmod(0o755)
    home = temp/'home'
    home.mkdir(mode=0o777)
    (home/'.config/opencode').mkdir(parents=True)
    workspace = temp/'workspace'
    workspace.mkdir(mode=0o777)
    provider = {'name': 'Synthetic transport only', 'package': '@opencode/ai/providers/openai-compatible', 'settings': {'baseURL': 'http://127.0.0.1:4000/v1', 'apiKey': 'synthetic'}, 'models': {'synthetic': {'modelID': 'synthetic-alias', 'name': 'Synthetic fixture', 'capabilities': {'tools': True, 'input': ['text'], 'output': ['text']}, 'limit': {'context': 200000, 'output': 16384}}}}
    config = {'providers': {'study2-synthetic': provider}, 'policies': [{'action': a, 'resource': '*', 'effect': 'deny'} for a in ['provider.use', 'mcp.use', 'skill.use', 'plugin.use']]+[{'action': 'provider.use', 'resource': 'study2-synthetic', 'effect': 'allow'}, {'action': 'tool.use', 'resource': 'task:*', 'effect': 'deny'}], 'agents': {'build': {'permissions': [{'action':'subagent','resource':'*','effect':'deny'}]}, 'title': {'model': 'study2-synthetic/synthetic'}}, 'snapshots': False}
    (home/'.config/opencode/opencode.json').write_text(json.dumps(config))
    socket = temp/'inference.sock'
    log = temp/'usage.jsonl'
    upstream = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Upstream)
    threading.Thread(target=upstream.serve_forever, daemon=True).start()
    gateway = proxy.UnixServer(str(socket), proxy.make_handler('synthetic-alias', f'http://127.0.0.1:{upstream.server_port}', key, log))
    socket.chmod(0o666)  # disposable synthetic-only socket; actual roles need scoped ownership
    threading.Thread(target=gateway.serve_forever, daemon=True).start()
    name = 'study2-native-transport-'+secrets.token_hex(4)
    launch = r'''
const {spawn}=require('child_process');
const bridge=spawn('node',['/tools/bridge.mjs','--socket','/run/study/inference.sock'],{stdio:['ignore','ignore','inherit']});
setTimeout(()=>{
 const cli=spawn('/tools/opencode',['run','--standalone','--model','study2-synthetic/synthetic','--format','json','--title','Synthetic denied delegation mechanics','--auto','Synthetic permission fixture: call explore subagent, then stop.'],{cwd:'/workspace',stdio:'inherit',env:{...process.env,HOME:'/home/node',PWD:'/workspace'}});
 cli.on('exit',code=>{process.exit(code??1);});
},300);
'''
    try:
        cmd = ['sudo','-n','podman','run','--rm','--init','--name',name,'--network','none','--memory','8g','--memory-swap','8g','--cpuset-cpus','0,1','--pids-limit','256','--cap-drop','ALL','--security-opt','no-new-privileges','--user','1000:1000','-e','HOME=/home/node','-v',f'{home}:/home/node:rw','-v',f'{workspace}:/workspace:rw','-v',f'{socket}:/run/study/inference.sock:ro','-v',f'{ROOT}/harness/container_http_bridge.mjs:/tools/bridge.mjs:ro','-v','/home/josh/.opencode/bin/opencode:/tools/opencode:ro','docker.io/library/node:24.19.0-bookworm-slim','node','-e',launch]
        result = subprocess.run(cmd,capture_output=True,text=True,timeout=90)
        events = [json.loads(l) for l in result.stdout.splitlines() if l.startswith('{')]
        rows = [json.loads(l) for l in log.read_text().splitlines()] if log.exists() else []
        tools = [e['part'] for e in events if e.get('type')=='tool_use']
        checks = {'cli_exit_zero': result.returncode==0,'two_upstream_calls':len(requests)==2,'delegation_denied':any(p.get('tool')=='subagent' and p.get('state',{}).get('status')=='error' and any(term in str(p['state']).lower() for term in ['denied','deny','not allowed','permission','no tool named']) for p in tools),'subagent_absent_from_catalog':all(t.get('function',{}).get('name')!='subagent' for r in requests for t in r.get('tools',[])), 'one_native_session_only':len({e['sessionID'] for e in events if e.get('sessionID')})==1,'final_text':any('SYNTHETIC_ADAPTER_READY' in e.get('part',{}).get('text','') for e in events),'native_final_stop':any(e.get('type')=='step_finish' and e['part'].get('reason')=='stop' for e in events),'two_usage_records':sum(r['event']=='usage' for r in rows)==2,'auto_tool_choice_not_forced':all('tool_choice' not in r or r['tool_choice'] in [None,'auto'] for r in requests),'no_secret_sent_by_cli':all('api_key' not in r for r in requests)}
        report = {'kind':'synthetic_native_adapter_mechanics_not_model_evaluation','model_calls':0,'checks':checks,'all_passed':all(checks.values()),'cli_exit_code':result.returncode,'native_session_ids':sorted({e['sessionID'] for e in events if e.get('sessionID')}),'tool_result_evidence':tools,'native_diagnostic_events':[e for e in events if e.get('type') not in ['step_start','step_finish','text','tool_use']], 'upstream_finish_reasons':[r.get('messages',[])[-1].get('role') for r in requests], 'native_step_count':sum(e.get('type')=='step_finish' for e in events),'tool_names_offered':sorted({t.get('function',{}).get('name','') for r in requests for t in r.get('tools',[])}),'subagent_tool_schema':next((t['function'].get('parameters') for r in requests for t in r.get('tools',[]) if t.get('function',{}).get('name')=='subagent'),None),'stderr':result.stderr,'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'harness/container_http_bridge.mjs',ROOT/'harness/unix_inference_proxy.py',Path(__file__)]},'qualification_limits':['synthetic responses only','no real provider/counter mapping qualification','no Context corpus or worker broker','ephemeral synthetic socket world-accessible inside isolated probe; actual roles require scoped ownership']}
    finally:
        subprocess.run(['sudo','-n','podman','rm','-f','-t','0',name],capture_output=True)
        gateway.shutdown();gateway.server_close();upstream.shutdown()
    report['elapsed_seconds_including_cleanup'] = time.monotonic()-start
    (ROOT/'setup/opencode-delegation-preliminary.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
    if not report['all_passed']:raise SystemExit(1)
