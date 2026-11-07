"""Normalize final provider usage without reconstructing native model splits.

Raw records stay authoritative. Multiple snapshots of the same provider response
are deduplicated by response ID; never add native/provider cross-checks together.
This draft does not infer actual model resolution or missing token counters.
"""
import copy
import hashlib
import json


def normalize(usage, *, run_id, session_id, actor_role, requested_model, response_id, mapping_id, phase):
    if not response_id:
        raise ValueError('A final usage snapshot needs a stable provider response ID')
    if not isinstance(usage, dict):
        raise ValueError('Expected raw provider usage object')
    details = usage.get('prompt_tokens_details') or {}
    output_details = usage.get('completion_tokens_details') or {}
    # cache_creation_tokens may alias cache_write_tokens. Choose one, never sum.
    writes = details.get('cache_write_tokens')
    if writes is None:
        writes = details.get('cache_creation_tokens')
    counters = {
        'inclusive_input_tokens': usage.get('prompt_tokens'),
        'billable_output_tokens': usage.get('completion_tokens'),
        'cached_input_tokens': details.get('cached_tokens'),
        'cache_write_tokens': writes,
        'diagnostic_reasoning_tokens': output_details.get('reasoning_tokens'),
    }
    for value in counters.values():
        if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < 0):
            raise ValueError('Invalid provider token counter')
    source = 'gateway_preserved_provider_usage'
    record_id = hashlib.sha256(f'{run_id}:{session_id}:{response_id}:{source}'.encode()).hexdigest()
    return {
        'schema_version': 1,
        'record_id': record_id,
        'run_id': run_id,
        'session_id': session_id,
        'parent_session_id': None,
        'actor_role': actor_role,
        'phase': phase,
        'requested_model': requested_model,
        'resolved_model': None,
        'actual_provider': None,
        'provider_response_id': response_id,
        'source': source,
        'counter_semantics': 'request_total_snapshot',
        'mapping_id': mapping_id,
        'billing_counters': counters,
        'reported_cost_usd': usage.get('cost'),
        'reasoning_rule': 'preserve_diagnostic_counter_do_not_add_to_completion',
        'raw_provider_usage': copy.deepcopy(usage),
        'native_usage': None,
        'reconciliation': 'provider_counters_only_native_join_and_resolution_unverified',
    }


def deduplicate(records):
    """Last snapshot by stable record ID; callers must preserve raw event order."""
    unique = {}
    for record in records:
        unique[record['record_id']] = record
    return list(unique.values())


if __name__ == '__main__':
    import sys
    payload = json.load(sys.stdin)
    print(json.dumps(normalize(**payload), indent=2))
