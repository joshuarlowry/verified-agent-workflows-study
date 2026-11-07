import json
import os
import signal
import subprocess
import sys
import time

request = json.loads(sys.stdin.buffer.readline())
work = request['work']
if work == 'partial':
    sys.stdout.write('{"public_response":"partial')
    sys.stdout.flush()
    sys.exit(7)
if work == 'huge':
    sys.stdout.write('x' * 1200000)
    sys.stdout.flush()
    time.sleep(2)
if work == 'tree':
    code = "import signal,time,pathlib; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(0.8); pathlib.Path('late-write').write_text('late')"
    subprocess.Popen([sys.executable, '-c', code])
    print('spawned', file=sys.stderr, flush=True)
    time.sleep(5)
if work == 'slow':
    time.sleep(5)
if work == 'control':
    print(json.dumps({'public_response': '\x01' * 16000}), flush=True)
    sys.exit(0)
if work == 'stderr':
    print('PRIVATE_CONTROLLER_DIAGNOSTIC_MARKER', file=sys.stderr, flush=True)
    sys.exit(2)
print(json.dumps({'public_response': 'public handoff: ' + work}), flush=True)
