"""Host-only candidate. The embedding controller is part of the trust boundary."""
import hashlib
import json
import os
import re
import selectors
import signal
import socket
import socketserver
import subprocess
import threading
import time
import uuid
from pathlib import Path

MAX_WIRE = 65536
MAX_OUTPUT = 1024 * 1024
MAX_TEXT = 16384
ID = re.compile(r'^[A-Za-z0-9_-]{1,80}$')
EXPECTED = ('google/gemma-4-31b-it', 'google/gemma-4-31b-it-20260402', 'Crusoe', 'crusoe/bf16', 'bf16')


def canonical(x):
    return json.dumps(x, ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode()


def strict_json(data):
    def pairs(items):
        d = {}
        for k, v in items:
            if k in d:
                raise ValueError('duplicate key')
            d[k] = v
        return d
    return json.loads(data, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('constant')))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_config(c, registration):
    """This verifies bindings, not the behavior of the command or inference gateway."""
    models = [m for m in registration['models'] if m['requested_id'] == EXPECTED[0]]
    if len(models) != 1 or EXPECTED[0] not in registration['setup_model_policy']['allowed_requested_ids']:
        raise ValueError('registration')
    m = models[0]
    keys = ('requested_id', 'resolved_id', 'provider', 'provider_tag', 'quantization')
    if tuple(m.get(k) for k in keys) != EXPECTED or tuple(c.get(k) for k in keys) != EXPECTED:
        raise ValueError('route')
    if m.get('allow_fallbacks') is not False or c.get('allow_fallbacks') is not False or m.get('zdr_required') is not True or c.get('zdr_required') is not True:
        raise ValueError('policy')
    # Null registration pins cannot validate real configuration. Synthetic mode is
    # deliberately explicit, for tests with fake children only, never study dispatch.
    if c.get('mode') not in ('synthetic', 'registered'):
        raise ValueError('mode')
    if c['mode'] == 'registered':
        for k in ('settings_sha256', 'full_harness_qualification_sha256'):
            if not isinstance(m.get(k), str) or c.get(k) != m[k] or not re.fullmatch(r'[a-f0-9]{64}', m[k]):
                raise ValueError('unfrozen registration')
        if not m.get('provider_pin_applied_to_study'):
            raise ValueError('unapplied pin')
        # No registered command/config manifest or qualified adapter exists here.
        # Never silently promote this synthetic candidate to real dispatch.
        raise ValueError('registered integration unavailable')
    for k in ('run_id', 'parent_session_id', 'baseline_id'):
        if not isinstance(c.get(k), str) or not ID.fullmatch(c[k]):
            raise ValueError('identity')
    if not isinstance(c.get('deadline_monotonic'), (int, float)) or isinstance(c['deadline_monotonic'], bool) or not (0 < c['deadline_monotonic'] < float('inf')):
        raise ValueError('deadline')
    argv = c.get('argv')
    hashes = c.get('file_hashes')
    if not isinstance(argv, list) or not argv or not all(isinstance(x, str) and x and '\x00' not in x for x in argv) or not os.path.isabs(argv[0]):
        raise ValueError('command')
    if not isinstance(hashes, dict) or argv[0] not in hashes or not hashes:
        raise ValueError('hashes')
    for p, h in hashes.items():
        if not os.path.isabs(p) or not isinstance(h, str) or not re.fullmatch(r'[a-f0-9]{64}', h) or sha(p) != h:
            raise ValueError('file hash')
    if c['mode'] == 'registered' and c.get('settings_path') not in hashes:
        raise ValueError('settings file')
    if c['mode'] == 'registered' and hashes[c['settings_path']] != m['settings_sha256']:
        raise ValueError('settings hash')
    for k in ('workspace', 'audit_dir', 'socket_path'):
        if not isinstance(c.get(k), str) or not os.path.isabs(c[k]):
            raise ValueError('path')
    if os.path.commonpath([os.path.realpath(c['workspace']), os.path.realpath(c['audit_dir'])]) == os.path.realpath(c['workspace']):
        raise ValueError('audit inside workspace')


def parent_native_final(event, session_id):
    """OpenCode JSON run event: only a step_finish/stop in the parent session."""
    if not isinstance(event, dict) or event.get('type') != 'step_finish':
        return False
    part = event.get('part')
    if not isinstance(part, dict) or part.get('reason') != 'stop':
        return False
    top, nested = event.get('sessionID'), part.get('sessionID')
    return (top == session_id or nested == session_id) and all(x in (None, session_id) for x in (top, nested))


class Broker:
    def __init__(self, config, registration, freeze, global_stop, handoff_refs):
        validate_config(config, registration)
        if not callable(freeze) or not callable(global_stop) or not callable(handoff_refs):
            raise ValueError('controller callbacks required')
        # Defensive deep copy: supervisor never obtains this configuration.
        self.c = json.loads(json.dumps(config))
        self.freeze = freeze
        self.global_stop = global_stop
        self.handoff_refs = handoff_refs
        self.lock = threading.RLock()
        self.audit_lock = threading.Lock()
        self.stop_lock = threading.Lock()
        self.stopped = None
        self.freeze_result = None
        self.requests = {}
        self.sessions = set()
        self.workers = threading.BoundedSemaphore(1)
        self.active = None
        self.closed = threading.Event()
        Path(self.c['audit_dir']).mkdir(mode=0o700, parents=True, exist_ok=True)
        self.audit_file = open(Path(self.c['audit_dir']) / 'broker.jsonl', 'x', encoding='utf-8')
        os.chmod(self.audit_file.name, 0o600)
        # Configuration contents/argv can contain secrets. Require a credential-free
        # config and record its fingerprint, not executable arguments or paths.
        self.audit('binding', run_id=self.c['run_id'], parent_session_id=self.c['parent_session_id'], baseline_id=self.c['baseline_id'], config_sha256=hashlib.sha256(canonical(self.c)).hexdigest(), usage_policy='raw separate views; no aggregation')
        self.monitor = threading.Thread(target=self._clock, daemon=True)
        self.monitor.start()

    def audit(self, kind, **fields):
        # Caller holds lock or is in construction. Never write credentials into config.
        row = {'kind': kind, 'utc_ns': time.time_ns(), 'monotonic_ns': time.monotonic_ns(), **fields}
        with self.audit_lock:
            self.audit_file.write(json.dumps(row, ensure_ascii=True, separators=(',', ':')) + '\n')
            self.audit_file.flush()

    def record_view(self, actor, kind, payload, request_id=None):
        """Trusted controller ingestion; never available over the supervisor socket."""
        if actor not in ('supervisor', 'worker') or kind not in ('prompt', 'event', 'native_usage', 'provider_usage', 'retry', 'check', 'revision', 'resolution'):
            raise ValueError('view')
        if request_id is not None and (not isinstance(request_id, str) or not ID.fullmatch(request_id)):
            raise ValueError('request id')
        encoded = canonical(payload)
        if len(encoded) > MAX_OUTPUT:
            raise ValueError('view too large')
        safe_copy = strict_json(encoded)
        with self.lock:
            if actor == 'worker' and request_id not in self.requests:
                raise ValueError('unknown worker request')
            self.audit('controller_view', actor=actor, view=kind, request_id=request_id, payload=safe_copy)

    def _clock(self):
        remaining = self.c['deadline_monotonic'] - time.monotonic()
        if not self.closed.wait(max(0, remaining)):
            self.stop('deadline')

    def _check_deadline_locked(self):
        if time.monotonic() >= self.c['deadline_monotonic'] and self.stopped is None:
            # Close admission immediately; the monitor executes termination/freeze.
            self.stopped = 'deadline'
            threading.Thread(target=self.stop, args=('deadline',), daemon=True).start()

    def request(self, msg):
        if not isinstance(msg, dict) or not isinstance(msg.get('op'), str):
            return {'error': 'invalid_request'}
        op = msg['op']
        allowed = {'call': {'op', 'request_id', 'work', 'session'}, 'get': {'op', 'request_id'}, 'cancel': {'op', 'request_id'}}
        if op not in allowed or set(msg) - allowed[op] or not isinstance(msg.get('request_id'), str) or not ID.fullmatch(msg['request_id']):
            return {'error': 'invalid_request'}
        rid = msg['request_id']
        with self.lock:
            self._check_deadline_locked()
            if op == 'get':
                return dict(self.requests[rid]['result']) if rid in self.requests else {'error': 'unknown_request'}
            if op == 'cancel':
                if rid not in self.requests:
                    return {'error': 'unknown_request'}
                r = self.requests[rid]
                if self.active == rid and not r.get('cancel'):
                    r['cancel'] = 'cancelled'
                    self.audit('cancel', request_id=rid)
                    self._signal(r, signal.SIGTERM)
                return dict(r['result'])
            if not isinstance(msg.get('work'), str) or not msg['work'] or len(msg['work'].encode('utf-8', errors='surrogatepass')) > MAX_TEXT:
                return {'error': 'invalid_request'}
            session = msg.get('session')
            if session is not None and (not isinstance(session, str) or not ID.fullmatch(session)):
                return {'error': 'invalid_request'}
            digest = hashlib.sha256(canonical({'work': msg['work'], 'session': session})).hexdigest()
            if rid in self.requests:
                r = self.requests[rid]
                return dict(r['result']) if r['digest'] == digest else {'error': 'id_conflict'}
            if self.stopped:
                return {'error': 'stopped', 'reason': self.stopped}
            if self.active:
                return {'error': 'busy'}
            if session is not None and session not in self.sessions:
                return {'error': 'unknown_session'}
            if not self.workers.acquire(blocking=False):
                return {'error': 'busy'}
            sid = session or uuid.uuid4().hex
            r = {'digest': digest, 'session': sid, 'result': {'request_id': rid, 'session': sid, 'status': 'running'}, 'done': threading.Event(), 'cancel': None, 'proc': None}
            self.requests[rid] = r
            self.active = rid
            self.audit('admit', request_id=rid, parent_session_id=self.c['parent_session_id'], worker_session_id=sid, work=msg['work'], continuation=session is not None, digest=digest)
            threading.Thread(target=self._run, args=(rid, msg['work']), daemon=True).start()
            return dict(r['result'])

    def _signal(self, r, sig):
        p = r.get('proc')
        if p:
            try:
                os.killpg(p.pid, sig)
            except ProcessLookupError:
                pass

    def _run(self, rid, work):
        r = self.requests[rid]
        status, public = 'worker_error', None
        selector = None
        try:
            # Launch and publish the PID while holding the same admission/stop lock.
            with self.lock:
                if r['cancel'] or self.stopped or time.monotonic() >= self.c['deadline_monotonic']:
                    r['cancel'] = r['cancel'] or self.stopped or 'deadline'
                    return
                # Recheck hashes before every spawn; immutable mounts are required to close TOCTOU.
                for p, h in self.c['file_hashes'].items():
                    if sha(p) != h:
                        raise ValueError('hash changed')
                p = subprocess.Popen(self.c['argv'], cwd=self.c['workspace'], env={'PATH': '/usr/bin:/bin', 'PWD': self.c['workspace'], 'LANG': 'C.UTF-8'}, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
                r['proc'] = p
                self.audit('spawn', request_id=rid, pid=p.pid)
            # Input is bounded; children must consume it promptly. Nonblocking writing avoids a stuck stdin.
            input_bytes = canonical({'work': work, 'worker_session_id': r['session'], 'parent_session_id': self.c['parent_session_id'], 'run_id': self.c['run_id'], 'baseline_id': self.c['baseline_id']}) + b'\n'
            os.set_blocking(p.stdin.fileno(), False)
            selector = selectors.DefaultSelector()
            selector.register(p.stdin, selectors.EVENT_WRITE, 'stdin')
            for stream, name in ((p.stdout, 'stdout'), (p.stderr, 'stderr')):
                os.set_blocking(stream.fileno(), False)
                selector.register(stream, selectors.EVENT_READ, name)
            pending = input_bytes
            output = bytearray()
            count = 0
            cancel_at = None
            exited_at = None
            while selector.get_map():
                with self.lock:
                    cancel = r['cancel'] or self.stopped
                if cancel:
                    if cancel_at is None:
                        cancel_at = time.monotonic()
                        self._signal(r, signal.SIGTERM)
                    if time.monotonic() - cancel_at >= 0.15:
                        self._signal(r, signal.SIGKILL)
                if p.poll() is not None:
                    # Kill remaining in-group tool descendants even after leader exit.
                    self._signal(r, signal.SIGKILL)
                    if exited_at is None:
                        exited_at = time.monotonic()
                    if time.monotonic() - exited_at > 1:
                        with self.lock:
                            r['cancel'] = r['cancel'] or 'output_limit'
                        break
                for key, _ in selector.select(0.05):
                    if key.data == 'stdin':
                        try:
                            n = os.write(key.fd, pending)
                            pending = pending[n:]
                        except (BrokenPipeError, OSError):
                            pending = b''
                        if not pending:
                            selector.unregister(key.fileobj)
                            key.fileobj.close()
                    else:
                        try:
                            chunk = os.read(key.fd, 8192)
                        except BlockingIOError:
                            continue
                        if not chunk:
                            selector.unregister(key.fileobj)
                            key.fileobj.close()
                            continue
                        count += len(chunk)
                        with self.lock:
                            self.audit('child_chunk', request_id=rid, stream=key.data, data_hex=chunk[:max(0, MAX_OUTPUT - (count-len(chunk)))].hex())
                        if key.data == 'stdout' and count <= MAX_OUTPUT:
                            output.extend(chunk)
                        if count > MAX_OUTPUT:
                            with self.lock:
                                r['cancel'] = r['cancel'] or 'output_limit'
                # A malicious escaped descendant holding pipes is bounded on cancellation.
                if cancel_at is not None and time.monotonic() - cancel_at > 1:
                    break
            p.wait(timeout=1)
            with self.lock:
                cancel = r['cancel'] or self.stopped
            if cancel:
                status = cancel if cancel in ('cancelled', 'deadline', 'output_limit') else 'interrupted'
            elif p.returncode == 0:
                # Adapter output is one complete public handoff object, not raw OpenCode events.
                obj = strict_json(bytes(output))
                if isinstance(obj, dict) and set(obj) == {'public_response'} and isinstance(obj['public_response'], str) and len(obj['public_response'].encode()) <= MAX_TEXT:
                    status, public = 'handoff', obj['public_response']
        except Exception as e:
            with self.lock:
                self.audit('worker_exception', request_id=rid, exception_type=type(e).__name__)
        finally:
            if selector:
                for key in list(selector.get_map().values()):
                    selector.unregister(key.fileobj)
                    key.fileobj.close()
                selector.close()
            if r['proc']:
                self._signal(r, signal.SIGKILL)
                try:
                    r['proc'].wait(timeout=1)
                except subprocess.TimeoutExpired:
                    status = 'worker_error'
            with self.lock:
                self._check_deadline_locked()
                if r['cancel'] or self.stopped:
                    why = r['cancel'] or self.stopped
                    status = why if why in ('cancelled', 'deadline', 'output_limit') else 'interrupted'
                    public = None
                result = {'request_id': rid, 'session': r['session'], 'status': status}
                if status == 'handoff':
                    try:
                        refs = self.handoff_refs(rid)
                        if not isinstance(refs, list) or len(refs) > 32 or not all(isinstance(x, dict) and set(x) == {'kind', 'ref'} and x['kind'] in ('change', 'check') and isinstance(x['ref'], str) and ID.fullmatch(x['ref']) for x in refs):
                            raise ValueError('references')
                        result['public_response'] = public
                        result['references'] = refs
                        if len(canonical(result)) + 1 > MAX_WIRE:
                            raise ValueError('response too large')
                        self.sessions.add(r['session'])
                    except Exception as e:
                        result.pop('public_response', None)
                        result.pop('references', None)
                        result['status'] = 'worker_error'
                        self.audit('reference_error', request_id=rid, exception_type=type(e).__name__)
                r['result'] = result
                try:
                    self.audit('finish', request_id=rid, result=result)
                finally:
                    self.active = None
                    self.workers.release()
                    r['done'].set()

    def stop(self, reason):
        if reason not in ('deadline', 'parent_final', 'user_stop', 'budget_exhausted', 'infrastructure_failure', 'protocol_violation'):
            raise ValueError('reason')
        # Serialize stop/freeze and make repeated calls idempotent.
        with self.stop_lock:
            if self.freeze_result is not None:
                return self.freeze_result
            with self.lock:
                if self.stopped is None:
                    self.stopped = reason
                reason = self.stopped
                self.audit('stop', reason=reason)
                r = self.requests.get(self.active)
                if r:
                    r['cancel'] = r['cancel'] or reason
                    self._signal(r, signal.SIGTERM)
            if reason == 'budget_exhausted':
                try:
                    self.global_stop(reason)
                except Exception as e:
                    with self.lock:
                        self.audit('global_stop_failed', exception_type=type(e).__name__)
            if r:
                r['done'].wait()  # no snapshot until the broker runner has reaped/closed
            try:
                # Controller must quiesce ALL writers and atomically freeze or raise.
                self.freeze(reason)
                outcome = 'frozen'
            except Exception as e:
                outcome = 'freeze_failed'
                with self.lock:
                    self.audit('freeze_exception', exception_type=type(e).__name__)
            with self.lock:
                self.freeze_result = outcome
                self.audit('freeze', reason=reason, outcome=outcome)
            return outcome

    def parent_event(self, event):
        if parent_native_final(event, self.c['parent_session_id']):
            return self.stop('parent_final')
        return None

    def close(self):
        if self.freeze_result is None:
            self.stop('infrastructure_failure')
        self.closed.set()
        self.monitor.join()
        with self.lock:
            self.audit_file.close()


class Server(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True
    request_queue_size = 16
    def __init__(self, broker):
        self.broker = broker
        self.slots = threading.BoundedSemaphore(16)
        super().__init__(broker.c['socket_path'], Handler)
        os.chmod(broker.c['socket_path'], 0o600)

    def process_request(self, request, client_address):
        if not self.slots.acquire(blocking=False):
            request.close()
            return
        try:
            super().process_request(request, client_address)
        except BaseException:
            self.slots.release()
            raise

    def process_request_thread(self, request, client_address):
        try:
            super().process_request_thread(request, client_address)
        finally:
            self.slots.release()


class Handler(socketserver.BaseRequestHandler):
    def handle(self):
        self.request.settimeout(2)
        try:
            buf = bytearray()
            while b'\n' not in buf and len(buf) <= MAX_WIRE:
                chunk = self.request.recv(min(8192, MAX_WIRE + 1 - len(buf)))
                if not chunk:
                    break
                buf.extend(chunk)
            if len(buf) > MAX_WIRE or not buf.endswith(b'\n') or buf.count(b'\n') != 1:
                response = {'error': 'invalid_request'}
            else:
                response = self.server.broker.request(strict_json(buf))
        except (ValueError, UnicodeError, OSError, RecursionError):
            response = {'error': 'invalid_request'}
        try:
            self.request.sendall(canonical(response) + b'\n')
        except OSError:
            pass
