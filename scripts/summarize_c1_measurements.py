"""Summarize recorded C1 clocks and accounting; never read patches or grade quality."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import sqlite3


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def seconds(start, end):
    if not start or not end:
        return None
    delta = end['monotonic_ns'] - start['monotonic_ns']
    if delta < 0:
        raise ValueError('Negative recorded duration')
    return delta / 1e9


def summarize(block):
    state = json.loads((block / 'collection.json').read_text())
    db = sqlite3.connect((block / 'study-ledger.sqlite').as_uri() + '?mode=ro', uri=True)
    rows = []
    try:
        for run in state['runs']:
            root = Path(run['root'])
            controller = root / 'controller.json'
            if not controller.exists():
                rows.append({'run_id': run['run_id'], 'arm': run['arm'],
                             'state': 'no_controller_endpoint_yet', 'usage': None})
                continue
            capture = json.loads(controller.read_text())
            native = capture.get('result', {}).get('native', {})
            events = [json.loads(x[0]) for x in db.execute(
                'SELECT body FROM events WHERE run=? ORDER BY seq', (run['run_id'],))]
            dispatch = next((x for x in events if x.get('kind') == 'dispatch'), None)
            terminal = next((x for x in events if x.get('kind') == 'terminal'), None)
            request_counts = db.execute(
                'SELECT COUNT(*),COUNT(response) FROM requests WHERE run=?', (run['run_id'],)).fetchone()
            usage_path = root / 'provider-resolution/raw-usage-summary.json'
            usage = json.loads(usage_path.read_text()) if usage_path.exists() else None
            roles = []
            if usage:
                for role in usage['roles']:
                    keys = ['role', 'native_session_ids', 'provider_successful_generations',
                            'native_unique_steps', 'known_input_inclusive_total', 'known_billable_output_total',
                            'cached_input_subset_total', 'cache_write_subset_total', 'diagnostic_reasoning_total',
                            'known_reported_cost_usd_subtotal', 'cost_complete',
                            'all_successes_have_native_step_count_match']
                    roles.append({**{k: role.get(k) for k in keys},
                                  'unknown_attempt_or_view_count': len(role['unknown_attempts_or_views']),
                                  'unknown_count_unit': 'capture views; not necessarily distinct billable calls'})
            rows.append({'run_id': run['run_id'], 'arm': run['arm'], 'repetition': run['repetition'],
                         'endpoint_reason': run.get('endpoint_reason'), 'dispatch': dispatch,
                         'first_native_event': native.get('first_event'), 'last_native_event': native.get('last_event'),
                         'native_process_exit': native.get('exit'), 'ledger_terminal': terminal,
                         'seconds': {'dispatch_to_terminal': seconds(dispatch, terminal),
                                     'dispatch_to_first_native_event': seconds(dispatch, native.get('first_event')),
                                     'dispatch_to_last_native_event': seconds(dispatch, native.get('last_event')),
                                     'dispatch_to_native_exit': seconds(dispatch, native.get('exit')),
                                     'workflow_setup_before_dispatch': seconds(run.get('controller_started'), dispatch),
                                     'between_workflow_backup': seconds(run.get('backup_started'), run.get('backup_ended'))},
                         'unique_worker_requests': request_counts[0], 'durable_worker_responses': request_counts[1],
                         'reply_delivery_failure_events': sum(x.get('kind') == 'worker_reply_delivery_failed' for x in events),
                         'operator_feedback_turns': None, 'active_human_effort_seconds': None,
                         'operator_measurement_limit': 'Not inferred from worker handoffs or model turns; requires separate operator action record.',
                         'roles': roles if usage else None,
                         'provenance': {'controller_sha256': digest(controller),
                                        'raw_usage_summary_sha256': digest(usage_path) if usage else None},
                         'quality': 'Not assessed by this report; final return and short runtime do not establish delivery.'})
    finally:
        db.close()
    return {'kind': 'recorded_C1_timing_and_usage_not_acceptance',
            'created_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'collection_status': state['status'], 'model_calls': 0, 'rows': rows,
            'billing_rule': 'Raw provider billing once, by role. Input includes cache subsets; reasoning is diagnostic and is not added to completion. Native/gateway/admin views are cross-checks, never additional charges.',
            'scope': 'Current clean block only; prior technical attempts and preparation overhead require separate attribution. Durations include tools/waits, not exclusive inference time. No acceptance or purchasing ranking.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--block', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    result = summarize(args.block.resolve(strict=True))
    with args.output.open('x') as out:
        json.dump(result, out, indent=2, allow_nan=False)
        out.write('\n')
    print(json.dumps({'output': str(args.output), 'rows': len(result['rows']), 'model_calls': 0}))
