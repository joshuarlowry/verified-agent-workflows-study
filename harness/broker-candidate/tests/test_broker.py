import importlib.machinery
import importlib.util
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from broker import Broker, Server, EXPECTED, parent_native_final, sha, validate_config

REG = json.loads((ROOT.parent / 'inputs/registration.json').read_text())
PYTHON = os.path.realpath(sys.executable)
WORKER = str(ROOT / 'tests/fake_worker.py')


class Fixture:
    def __init__(self, seconds=4):
        self.tmp = tempfile.TemporaryDirectory(dir='/tmp/opencode')
        base = Path(self.tmp.name)
        self.ws = base / 'ws'
        self.ws.mkdir()
        self.frozen = []
        self.global_stops = []
        self.config = dict(zip(('requested_id', 'resolved_id', 'provider', 'provider_tag', 'quantization'), EXPECTED))
        self.config.update(mode='synthetic', allow_fallbacks=False, zdr_required=True, run_id='run', parent_session_id='parent', baseline_id='base', deadline_monotonic=time.monotonic() + seconds, argv=[PYTHON, WORKER], file_hashes={PYTHON: sha(PYTHON), WORKER: sha(WORKER)}, workspace=str(self.ws), audit_dir=str(base / 'audit'), socket_path=str(base / 'socket'))
        self.b = Broker(self.config, REG, self.freeze, self.global_stops.append, lambda rid: [{'kind': 'change', 'ref': 'same_workspace_1'}])
        self.s = Server(self.b)
        self.thread = threading.Thread(target=self.s.serve_forever, kwargs={'poll_interval': 0.01})
        self.thread.start()

    def freeze(self, reason):
        self.frozen.append((reason, time.monotonic()))

    def wire(self, msg):
        return self.raw(json.dumps(msg).encode() + b'\n')

    def raw(self, data):
        with socket.socket(socket.AF_UNIX) as s:
            s.settimeout(3)
            s.connect(self.config['socket_path'])
            s.sendall(data)
            result = b''
            while not result.endswith(b'\n'):
                part = s.recv(65536)
                if not part:
                    break
                result += part
            return json.loads(result)

    def wait(self, rid, seconds=3):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            r = self.wire({'op': 'get', 'request_id': rid})
            if r.get('status') != 'running':
                return r
            time.sleep(.01)
        self.fail('wait expired')

    def fail(self, msg):
        raise AssertionError(msg)

    def close(self):
        self.s.shutdown()
        self.s.server_close()
        self.thread.join()
        self.b.close()
        self.tmp.cleanup()


class BrokerTests(unittest.TestCase):
    def setUp(self):
        self.f = Fixture()

    def tearDown(self):
        self.f.close()

    def call(self, rid, work, **extra):
        return self.f.wire({'op': 'call', 'request_id': rid, 'work': work, **extra})

    def test_success_idempotency_continuation(self):
        r = self.call('a', 'hello')
        self.assertEqual(r['status'], 'running')
        done = self.f.wait('a')
        self.assertEqual(done['status'], 'handoff')
        self.assertEqual(done['references'], [{'kind': 'change', 'ref': 'same_workspace_1'}])
        self.assertEqual(self.call('a', 'hello'), done)
        self.assertEqual(self.call('a', 'other')['error'], 'id_conflict')
        self.assertEqual(self.call('b', 'next', session='unknown')['error'], 'unknown_session')
        s = self.call('b', 'next', session=done['session'])['session']
        self.assertEqual(s, done['session'])
        self.assertEqual(self.f.wait('b')['status'], 'handoff')
        new = self.call('c', 'new')['session']
        self.assertNotEqual(s, new)
        self.f.wait('c')
        audit = Path(self.f.config['audit_dir'], 'broker.jsonl').read_text()
        self.assertEqual(audit.count('"kind":"spawn"'), 3)
        self.assertFalse(self.f.frozen)  # handoff is not parent completion

    def test_invalid_and_override(self):
        for field, value in [('model', EXPECTED[0]), ('argv', ['/bin/sh']), ('workspace', '/elsewhere'), ('deadline', 99999), ('provider', 'other'), ('run_id', 'evil'), ('role', 'worker')]:
            self.assertEqual(self.call('x', 'hello', **{field: value}), {'error': 'invalid_request'})
        self.assertEqual(self.f.raw(b'{"op":"get","request_id":"x","op":"call"}\n'), {'error': 'invalid_request'})
        self.assertEqual(self.f.raw(b'x' * 65537 + b'\n'), {'error': 'invalid_request'})
        self.assertEqual(self.f.wire({'op': 'get', 'request_id': 'unknown'}), {'error': 'unknown_request'})
        self.assertEqual(self.f.wire({'op': 'call', 'request_id': '../x', 'work': 'x'}), {'error': 'invalid_request'})
        for key, value in [('provider_tag', 'coreweave/fp4'), ('requested_id', 'other'), ('allow_fallbacks', True), ('file_hashes', {PYTHON: '0' * 64}), ('mode', 'registered')]:
            bad = dict(self.f.config, **{key: value})
            with self.assertRaises(ValueError):
                validate_config(bad, REG)
        hypothetical = json.loads(json.dumps(REG))
        model = next(m for m in hypothetical['models'] if m['requested_id'] == EXPECTED[0])
        model.update(settings_sha256='a' * 64, full_harness_qualification_sha256='b' * 64, provider_pin_applied_to_study=True)
        with self.assertRaisesRegex(ValueError, 'registered integration unavailable'):
            validate_config(dict(self.f.config, mode='registered', settings_sha256='a' * 64, full_harness_qualification_sha256='b' * 64), hypothetical)

    def test_partial_and_private_stderr(self):
        self.call('partial', 'partial')
        r = self.f.wait('partial')
        self.assertEqual(r['status'], 'worker_error')
        self.assertNotIn('public_response', r)
        self.call('error', 'stderr')
        r = self.f.wait('error')
        self.assertEqual(r['status'], 'worker_error')
        self.assertNotIn('PRIVATE_CONTROLLER', json.dumps(r))
        audit = Path(self.f.config['audit_dir'], 'broker.jsonl').read_text()
        self.assertIn('child_chunk', audit)
        self.assertIn('50524956415445', audit.upper())

    def test_overlap_cancel_tree(self):
        self.call('tree', 'tree')
        self.assertEqual(self.call('overlap', 'hello')['error'], 'busy')
        time.sleep(.15)
        self.assertEqual(self.f.wire({'op': 'cancel', 'request_id': 'tree'})['status'], 'running')
        self.assertEqual(self.f.wait('tree')['status'], 'cancelled')
        time.sleep(1)
        self.assertFalse((self.f.ws / 'late-write').exists())
        self.call('after', 'hello')
        self.assertEqual(self.f.wait('after')['status'], 'handoff')

    def test_parent_native_final_and_freeze(self):
        self.call('tree', 'tree')
        time.sleep(.15)
        self.assertIsNone(self.f.b.parent_event({'type': 'text', 'sessionID': 'parent'}))
        self.assertIsNone(self.f.b.parent_event({'type': 'step_finish', 'part': {'sessionID': 'child', 'reason': 'stop'}}))
        self.assertIsNone(self.f.b.parent_event({'type': 'step_finish', 'part': {'sessionID': 'parent', 'reason': 'tool-calls'}}))
        self.assertEqual(self.f.b.parent_event({'type': 'step_finish', 'part': {'sessionID': 'parent', 'reason': 'stop'}}), 'frozen')
        self.assertEqual(self.f.wait('tree')['status'], 'interrupted')
        self.assertEqual(self.call('later', 'x')['reason'], 'parent_final')
        self.assertEqual(self.f.b.stop('user_stop'), 'frozen')
        self.assertEqual(len(self.f.frozen), 1)
        time.sleep(1)
        self.assertFalse((self.f.ws / 'late-write').exists())

    def test_controller_views_separate_and_resolution(self):
        self.call('views', 'hello')
        self.f.wait('views')
        self.f.b.record_view('supervisor', 'native_usage', {'tokens': 11})
        self.f.b.record_view('worker', 'native_usage', {'tokens': 7}, 'views')
        self.f.b.record_view('worker', 'provider_usage', {'completion_tokens': 9, 'response_id': 'synthetic'}, 'views')
        with self.assertRaises(ValueError):
            self.f.b.record_view('worker', 'provider_usage', {}, 'unknown')
        rows = [json.loads(x) for x in Path(self.f.config['audit_dir'], 'broker.jsonl').read_text().splitlines()]
        views = [x for x in rows if x['kind'] == 'controller_view']
        self.assertEqual([(x['actor'], x['view']) for x in views], [('supervisor', 'native_usage'), ('worker', 'native_usage'), ('worker', 'provider_usage')])
        self.assertTrue(parent_native_final({'type': 'step_finish', 'sessionID': 'parent', 'part': {'reason': 'stop'}}, 'parent'))
        self.assertFalse(parent_native_final({'type': 'step_finish', 'sessionID': 'child', 'part': {'sessionID': 'parent', 'reason': 'stop'}}, 'parent'))

    def test_budget_stop_and_freeze_failure(self):
        self.f.b.freeze = lambda reason: (_ for _ in ()).throw(RuntimeError('private error'))
        self.assertEqual(self.f.b.stop('budget_exhausted'), 'freeze_failed')
        self.assertEqual(self.f.global_stops, ['budget_exhausted'])
        self.assertEqual(self.call('later', 'x')['reason'], 'budget_exhausted')
        self.assertNotIn('private error', json.dumps(self.call('later2', 'x')))

    def test_output_limit(self):
        self.call('large', 'huge')
        self.assertEqual(self.f.wait('large')['status'], 'output_limit')

    def test_public_response_wire_bound(self):
        self.call('ctrl', 'control')
        r = self.f.wait('ctrl')
        self.assertEqual(r['status'], 'worker_error')
        self.assertNotIn('public_response', r)

    def test_cli(self):
        loader = importlib.machinery.SourceFileLoader('cli', str(ROOT / 'gemma-broker'))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        mod = importlib.util.module_from_spec(spec)
        loader.exec_module(mod)
        self.assertEqual(mod.SOCKET, '/run/study/gemma-broker.sock')
        mod.SOCKET = self.f.config['socket_path']  # test only; production has no override
        class Input:
            buffer = io.BytesIO(b'hello')
        old = sys.stdin
        try:
            sys.stdin = Input()
            r, code = mod.main(['call', 'cli-id'])
        finally:
            sys.stdin = old
        self.assertEqual(code, 0)
        self.assertEqual(r['status'], 'running')
        self.assertEqual(self.f.wait('cli-id')['status'], 'handoff')
        self.assertEqual(mod.main(['get', 'cli-id', '/evil'])[1], 2)
        proc = subprocess.run([str(ROOT / 'gemma-broker'), 'call', '../evil'], capture_output=True)
        self.assertEqual(proc.returncode, 2)


class DeadlineTests(unittest.TestCase):
    def test_absolute_deadline_no_reset_and_admission_race(self):
        f = Fixture(.55)
        try:
            f.wire({'op': 'call', 'request_id': 'one', 'work': 'hello'})
            self.assertEqual(f.wait('one')['status'], 'handoff')
            time.sleep(.25)
            f.wire({'op': 'call', 'request_id': 'two', 'work': 'tree'})
            r = f.wait('two')
            self.assertEqual(r['status'], 'deadline')
            self.assertEqual(f.wire({'op': 'call', 'request_id': 'three', 'work': 'hello'})['reason'], 'deadline')
            end = time.monotonic() + 2
            while not f.frozen and time.monotonic() < end:
                time.sleep(.01)
            self.assertEqual(f.frozen[0][0], 'deadline')
            time.sleep(.9)
            self.assertFalse((f.ws / 'late-write').exists())
        finally:
            f.close()

    def test_stop_call_race(self):
        f = Fixture()
        try:
            barrier = threading.Barrier(3)
            responses = []
            def caller():
                barrier.wait()
                responses.append(f.wire({'op': 'call', 'request_id': 'race', 'work': 'tree'}))
            def stopper():
                barrier.wait()
                f.b.stop('user_stop')
            threads = [threading.Thread(target=caller), threading.Thread(target=stopper)]
            for t in threads: t.start()
            barrier.wait()
            for t in threads: t.join(3)
            self.assertTrue(all(not t.is_alive() for t in threads))
            self.assertIn(responses[0].get('status', responses[0].get('error')), ('running', 'stopped'))
            self.assertEqual(len(f.frozen), 1)
            self.assertEqual(f.wire({'op': 'call', 'request_id': 'after', 'work': 'x'})['error'], 'stopped')
        finally:
            f.close()


if __name__ == '__main__':
    unittest.main(verbosity=2)
