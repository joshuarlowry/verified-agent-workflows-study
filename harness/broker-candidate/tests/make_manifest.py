"""Generate the endpoint manifest; not a signature or evidence of review."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
out = root / 'broker-candidate'
files = sorted(p for base in (root / 'inputs', out) for p in base.rglob('*') if p.is_file() and p.name != 'BROKER_MANIFEST.json' and '__pycache__' not in p.parts)
entries = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
manifest = {
    'kind': 'construction_endpoint_not_qualified',
    'author': {'requested_model': 'openai/gpt-6.1-terra', 'provider_reported': 'Azure', 'reasoning': 'high', 'harness_identity': 'study2-terra-fixture-review/terra', 'actual_resolution': None},
    'different_authorized_model_review': 'pending',
    'model_calls': 0,
    'scored_or_calibration_dispatches': 0,
    'sha256_by_path': entries,
    'hash_scope': 'all regular inputs and candidate files except manifest itself and Python bytecode; SHA-256 of bytes; manifest not self-hashed',
    'commands': [
        {'cwd': '/workspace/broker-candidate', 'command': 'set -o pipefail; python3 -B -m unittest discover -s tests -v 2>&1 | tee records/test-first.log', 'exit_code': 0, 'result': '10 tests passed'},
        {'cwd': '/workspace/broker-candidate', 'command': 'set -o pipefail; python3 -B -m unittest discover -s tests -v 2>&1 | tee records/test-wire-first-failure.log', 'exit_code': 1, 'result': '11 tests, one failure: oversized escaped response accepted'},
        {'cwd': '/workspace/broker-candidate', 'command': 'set -o pipefail; python3 -B -m unittest discover -s tests -v 2>&1 | tee records/test-after-wire-fix.log', 'exit_code': 0, 'result': '11 tests passed after response serialization bound fix'},
        {'cwd': '/workspace/broker-candidate', 'command': 'set -o pipefail; python3 -B -m unittest discover -s tests -v 2>&1 | tee records/test-final.log', 'exit_code': 0, 'result': '12 tests passed after further controller capture and event changes'},
        {'cwd': '/workspace/broker-candidate', 'command': 'set -o pipefail; python3 -B -m unittest discover -s tests -v 2>&1 | tee records/test-endpoint.log', 'exit_code': 0, 'result': '12 tests passed including hypothetical filled-registration refusal'},
        {'cwd': '/workspace/broker-candidate', 'command': 'set -o pipefail; python3 -B -m unittest discover -s tests -v 2>&1 | tee records/test-endpoint-2.log', 'exit_code': 0, 'result': '12 tests passed after deadline publication and cleanup tightening'},
        {'cwd': '/workspace', 'command': 'date --iso-8601=seconds', 'exit_code': 0, 'result': '2026-11-07T04:41:41+00:00'},
        {'cwd': '/workspace', 'command': 'python3 -B broker-candidate/tests/make_manifest.py', 'exit_code': 0, 'result': 'generated this manifest'},
    ],
    'limits': ['synthetic fake processes only', 'registered mode deliberately disabled', 'no real OpenCode, provider, container, controller, global budget or snapshot qualification', 'GLM-only usage helper U4/U5 unresolved and not forked'],
}
(out / 'BROKER_MANIFEST.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=True) + '\n')
