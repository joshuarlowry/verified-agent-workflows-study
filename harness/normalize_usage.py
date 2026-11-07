"""Draft final-usage normalization, revision 2 (not broker-qualified).

Only the observed GLM/Relace mapping is registered here so far. Preserve raw
snapshots and fail on attribution/counter conflicts rather than guessing or
silently double charging. Controller evidence still supplies actual provenance.
"""
import copy
import hashlib
import json
import math

QUALIFIED_MAPPINGS = {
    'glm-relace-completion-only-r7': {
        'requested_model': 'z-ai/glm-5.3-flash',
        'provider_tag': 'relace/fp4',
        'evidence': 'readiness/revision7-provider-and-accounting.json',
    },
}
ROLES = {'complete_agent', 'supervisor', 'worker', 'builder', 'cross_reviewer', 'coordinator', 'evaluator'}
PHASES = {'mechanical_preflight', 'construction', 'cross_review', 'calibration', 'scored', 'evaluation'}
SOURCE = 'captured_gateway_usage'


class ReconciliationError(ValueError):
    """Caller must retain original raw records and report unresolved usage."""


def _text(value, name):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{name} must be a nonempty string')


def _identity(run_id, session_id, response_id):
    # Canonical tuple serialization avoids delimiter collisions in caller IDs.
    encoded = json.dumps([run_id, session_id, response_id, SOURCE], ensure_ascii=False, separators=(',', ':')).encode()
    return hashlib.sha256(encoded).hexdigest()


def _object(value, name):
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f'{name} must be an object or null')
    return value


def normalize(usage, *, run_id, session_id, actor_role, requested_model,
              response_id, mapping_id, provider_tag, phase):
    for name, value in [('run_id', run_id), ('session_id', session_id), ('response_id', response_id), ('actor_role', actor_role), ('phase', phase), ('mapping_id', mapping_id), ('provider_tag', provider_tag), ('requested_model', requested_model)]:
        _text(value, name)
    if actor_role not in ROLES or phase not in PHASES:
        raise ValueError('Unregistered actor role or phase')
    mapping = QUALIFIED_MAPPINGS.get(mapping_id)
    if not mapping or mapping['requested_model'] != requested_model or mapping['provider_tag'] != provider_tag:
        raise ValueError('Unqualified mapping/model/provider combination')
    if not isinstance(usage, dict):
        raise ValueError('Expected raw provider usage object')
    # Reject non-JSON/nonfinite values without changing the retained raw input.
    try:
        json.dumps(usage, allow_nan=False)
    except (ValueError, TypeError) as error:
        raise ValueError('Raw usage is not finite JSON') from error
    details = _object(usage.get('prompt_tokens_details'), 'prompt_tokens_details')
    output_details = _object(usage.get('completion_tokens_details'), 'completion_tokens_details')
    writes = details.get('cache_write_tokens')
    creation = details.get('cache_creation_tokens')
    for value in (writes, creation):
        if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < 0):
            raise ValueError('Invalid cache alias counter')
    if writes is not None and creation is not None and writes != creation:
        raise ReconciliationError('Conflicting cache-write/creation aliases')
    if writes is None:
        writes = creation
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
    cost = usage.get('cost')
    if cost is not None and (isinstance(cost, bool) or not isinstance(cost, (int, float)) or not math.isfinite(cost) or cost < 0):
        raise ValueError('Cost must be finite and nonnegative, or null')
    return {
        'schema_version': 2,
        'record_id': _identity(run_id, session_id, response_id),
        'run_id': run_id,
        'session_id': session_id,
        'parent_session_id': None,
        'actor_role': actor_role,
        'phase': phase,
        'requested_model': requested_model,
        'expected_provider_tag': provider_tag,
        'resolved_model': None,
        'actual_provider': None,
        'provider_response_id': response_id,
        'source': SOURCE,
        'counter_semantics': 'final_request_total_observation',
        'mapping_id': mapping_id,
        'mapping_evidence': mapping['evidence'],
        'billing_counters': counters,
        'reported_cost_usd': cost,
        'reasoning_rule': 'preserve_diagnostic_counter_do_not_add_to_completion',
        'raw_provider_usage_snapshots': [copy.deepcopy(usage)],
        'normalization_warnings': [],
        'native_usage': None,
        'reconciliation': 'provider_counters_only_native_join_and_resolution_unverified',
    }


def deduplicate(records):
    """Conservative reconciliation of final observations; never discard conflicts.

    A provider response attributed to multiple actors/sessions is unresolved,
    rather than two charges. Missing later fields cannot erase known values;
    raw observations and a warning are retained. Changed known totals conflict.
    """
    unique = {}
    identity_fields = ['record_id', 'run_id', 'session_id', 'actor_role', 'phase',
                       'requested_model', 'expected_provider_tag', 'mapping_id']
    for original in records:
        row = copy.deepcopy(original)
        if row.get('source') != SOURCE:
            raise ReconciliationError('Unregistered usage source')
        if row.get('record_id') != _identity(row['run_id'], row['session_id'], row['provider_response_id']):
            raise ReconciliationError('Record identity does not match canonical fields')
        key = (row['source'], row['provider_response_id'])
        if key not in unique:
            unique[key] = row
            continue
        previous = unique[key]
        if any(previous.get(name) != row.get(name) for name in identity_fields):
            raise ReconciliationError('Conflicting response attribution or mapping')
        for field in previous['billing_counters']:
            old = previous['billing_counters'][field]
            new = row['billing_counters'][field]
            if old is not None and new is not None and old != new:
                raise ReconciliationError('Conflicting final token totals')
            if old is None:
                previous['billing_counters'][field] = new
            elif new is None:
                previous['normalization_warnings'].append('incomplete_duplicate_did_not_erase_known_counter')
        old = previous['reported_cost_usd']; new = row['reported_cost_usd']
        if old is not None and new is not None and old != new:
            raise ReconciliationError('Conflicting final reported costs')
        if old is None:
            previous['reported_cost_usd'] = new
        elif new is None:
            previous['normalization_warnings'].append('incomplete_duplicate_did_not_erase_known_cost')
        for snapshot in row['raw_provider_usage_snapshots']:
            if snapshot not in previous['raw_provider_usage_snapshots']:
                previous['raw_provider_usage_snapshots'].append(snapshot)
        previous['normalization_warnings'] = sorted(set(previous['normalization_warnings']))
    return list(unique.values())


if __name__ == '__main__':
    import sys
    payload = json.load(sys.stdin)
    print(json.dumps(normalize(**payload), indent=2, allow_nan=False))
