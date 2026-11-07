"""GLM usage cross-review diagnostic (revision 2), authored by this review session.

Unapproved non-authoritative scratch diagnostic; no model API calls.
Run: python3 -B diagnostics/usage-cross-review-diagnostic.py  (cwd = scratch root)
Exit 0: every expected outcome confirmed. Exit 1: expectation failed (candidate defect).
"""
import copy, json, math, sys
from decimal import Decimal
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'inputs' / 'harness'))
from normalize_usage import normalize, deduplicate, ReconciliationError  # noqa: E402

SCHEMA = json.loads((ROOT / 'inputs/schemas/provider-usage-record.schema.json').read_text())
READINESS = json.loads((ROOT / 'inputs/readiness/revision7-provider-and-accounting.json').read_text())

results = []
def check(name, expected, actual):
    ok = expected == actual
    results.append((name, ok))
    print(('PASS' if ok else 'FAIL') + ' ' + name + ('' if ok else f'  expected={expected!r} actual={actual!r}'))
    return ok

def rejects(fn):
    try:
        fn()
        return 'accepted'
    except Exception as e:
        return type(e).__name__

base = dict(run_id='run', session_id='session', actor_role='coordinator',
            requested_model='z-ai/glm-5.3-flash', response_id='scratch-synthetic',
            mapping_id='glm-relace-completion-only-r7', provider_tag='relace/fp4',
            phase='mechanical_preflight')
def row(usage, **ch): return normalize(usage, **{**base, **ch})

# --- 1. r7 evidence replay (synthetic scratch response ids, not real ones) ---
r7 = READINESS['glm_adapter']['provider_usage']
ids = ['scratch-diag-r7-call-1', 'scratch-diag-r7-call-2', 'scratch-diag-r7-call-3']
expect = [(5005, 245, 384, 0, 272, 0.0001647555), (5257, 13, 5120, 0, 0, 0.0001504987), (5279, 6, 5248, 0, 0, 0.0001504774)]
for i, (u, rid, exp) in enumerate(zip(r7, ids, expect)):
    payload = u['usage']
    before = copy.deepcopy(payload)
    rec = row(payload, response_id=rid)
    jsonschema.validate(rec, SCHEMA)
    check(f'r7[{i}] counters completion-only', exp,
          (rec['billing_counters']['inclusive_input_tokens'], rec['billing_counters']['billable_output_tokens'],
           rec['billing_counters']['cached_input_tokens'], rec['billing_counters']['cache_write_tokens'],
           rec['billing_counters']['diagnostic_reasoning_tokens'], rec['reported_cost_usd']))
    check(f'r7[{i}] usage not mutated', before, payload)
    check(f'r7[{i}] resolved/provider/native null (declared gap)',
          (rec['resolved_model'], rec['actual_provider'], rec['native_usage'], rec['parent_session_id']),
          (None, None, None, None))
    check(f'r7[{i}] reasoning_rule + reconciliation consts',
          (rec['reasoning_rule'], rec['reconciliation']),
          ('preserve_diagnostic_counter_do_not_add_to_completion',
           'provider_counters_only_native_join_and_resolution_unverified'))

# --- 2. completion-only arithmetic recomputation (from immutable evidence) ---
hist = READINESS['historical_bill_recomputation']
pr = Decimal(hist['prompt_usd_per_token']); cr = Decimal(hist['completion_usd_per_token'])
co = pr * hist['prompt_tokens'] + cr * hist['completion_tokens']
cpr = pr * hist['prompt_tokens'] + cr * (hist['completion_tokens'] + hist['reasoning_tokens'])
check('hist completion-only == provider-reported', Decimal(hist['provider_reported_cost_usd']), co)
check('hist completion+reasoning differs (not billed)', Decimal(hist['completion_only_cost_usd']) != Decimal(hist['completion_plus_reasoning_cost_usd']), True)
check('hist completion+reasoning arithmetic', Decimal(hist['completion_plus_reasoning_cost_usd']), cpr)
for i, b in enumerate(READINESS['billing_recomputations']):
    check(f'r7 recomputation[{i}] reported==completion_only',
          Decimal(b['reported_cost_usd']) == Decimal(b['completion_only_cost_usd']), b['completion_only_matches'])
    if b['reasoning_tokens'] > 0:
        check(f'r7 recomputation[{i}] adding reasoning would overbill', Decimal(b['completion_plus_reasoning_cost_usd']) != Decimal(b['reported_cost_usd']), True)

# --- 3. historical usage replay (19/89/104, reported cost preserved verbatim) ---
hist_usage = {'prompt_tokens': 19, 'completion_tokens': 89,
              'completion_tokens_details': {'reasoning_tokens': 104},
              'prompt_tokens_details': {'cache_write_tokens': 7, 'cache_creation_tokens': 7},
              'cost': 0.0000087543}
rec = row(hist_usage, response_id='scratch-diag-historical')
jsonschema.validate(rec, SCHEMA)
check('hist 89/104 kept separate, cost verbatim',
      (rec['billing_counters']['billable_output_tokens'], rec['billing_counters']['diagnostic_reasoning_tokens'],
       rec['billing_counters']['cache_write_tokens'], rec['reported_cost_usd']),
      (89, 104, 7, 0.0000087543))

# --- 4. U1 collision fix ---
a = row({}, run_id='a:b', session_id='c'); b = row({}, run_id='a', session_id='b:c')
check('colon-join collision now distinct ids', a['record_id'] != b['record_id'], True)
exotic = [('a"b', 'c\\d'), ('x,y', 'z\nw'), ('é', 'é')]
for i, (r_, s_) in enumerate(exotic):
    p = row({}, run_id=r_, session_id=s_); q = row({}, run_id=s_, session_id=r_)
    check(f'exotic identity distinct[{i}]', p['record_id'] != q['record_id'], True)
check('cross-session same response conflicts (not dropped, not double charge)',
      rejects(lambda: deduplicate([a, b])), 'ReconciliationError')
check('same identity different mapping conflicts',
      rejects(lambda: deduplicate([row({}, response_id='rr', mapping_id='glm-relace-completion-only-r7'),
                                   row({}, response_id='rr', run_id='run2')])), 'ReconciliationError')
tampered = row({}); tampered['record_id'] = 'f' * 64
check('tampered record_id rejected', rejects(lambda: deduplicate([tampered])), 'ReconciliationError')

# --- 5. deduplicate merge semantics ---
full = row(hist_usage, response_id='scratch-dedupe-full')
inc = row({}, response_id='scratch-dedupe-full')
before_inputs = copy.deepcopy([full, inc])
merged = deduplicate([full, inc])
check('deduplicate does not mutate inputs', before_inputs, [copy.deepcopy(full), copy.deepcopy(inc)])
m = merged[0]
check('incomplete duplicate retains known counters',
      (m['billing_counters']['billable_output_tokens'], m['billing_counters']['diagnostic_reasoning_tokens'],
       m['billing_counters']['cache_write_tokens'], m['reported_cost_usd']), (89, 104, 7, 0.0000087543))
check('both raw snapshots retained + warning', (len(m['raw_provider_usage_snapshots']), bool(m['normalization_warnings'])), (2, True))
jsonschema.validate(m, SCHEMA)
check('incomplete duplicate warnings deduped+sorted', m['normalization_warnings'],
      ['incomplete_duplicate_did_not_erase_known_cost', 'incomplete_duplicate_did_not_erase_known_counter'])
check('changed known counter rejected', rejects(lambda: deduplicate([full, row({'completion_tokens': 90, 'cost': 0.0000087543,
      'prompt_tokens_details': {'cache_write_tokens': 7, 'cache_creation_tokens': 7},
      'completion_tokens_details': {'reasoning_tokens': 104}}, response_id='scratch-dedupe-full')])), 'ReconciliationError')
check('changed known cost rejected', rejects(lambda: deduplicate([full, row({'completion_tokens': 89, 'cost': 0.0000087544,
      'prompt_tokens_details': {'cache_write_tokens': 7, 'cache_creation_tokens': 7},
      'completion_tokens_details': {'reasoning_tokens': 104}}, response_id='scratch-dedupe-full')])), 'ReconciliationError')
check('identical duplicates collapse to one', len(deduplicate([full, copy.deepcopy(full)])), 1)
check('identical duplicates add no warnings', deduplicate([full, copy.deepcopy(full)])[0]['normalization_warnings'], [])
three = deduplicate([full, inc, inc])
check('chain merges keep counters + deduped warnings', (three[0]['billing_counters']['billable_output_tokens'],
      three[0]['normalization_warnings']), (89, ['incomplete_duplicate_did_not_erase_known_cost',
                                                 'incomplete_duplicate_did_not_erase_known_counter']))
late_known = deduplicate([row({}, response_id='scratch-fill'), row({'completion_tokens': 5}, response_id='scratch-fill')])
check('later known counter fills null without warning',
      (late_known[0]['billing_counters']['billable_output_tokens'], late_known[0]['normalization_warnings']), (5, []))
distinct_raw = deduplicate([full, row({'prompt_tokens': 19, 'completion_tokens': 89, 'total_tokens': 108, 'cost': 0.0000087543,
      'prompt_tokens_details': {'cache_write_tokens': 7, 'cache_creation_tokens': 7},
      'completion_tokens_details': {'reasoning_tokens': 104}}, response_id='scratch-dedupe-full')])
check('distinct raw snapshots both retained on equal counters', len(distinct_raw[0]['raw_provider_usage_snapshots']), 2)
# warnings-merge asymmetry probe (candidate minor defect): simulate output of a prior
# reconciliation pass carrying a warning, then re-merge it as the LATER duplicate.
wrec = deduplicate([full, inc])[0]
wrec['normalization_warnings'].append('custom_warning_from_prior_pass')
fresh_inc = row({}, response_id='scratch-dedupe-full')  # same response id, empty counters
remerged = deduplicate([fresh_inc, wrec])
check('incoming warnings from later duplicate preserved?',
      'custom_warning_from_prior_pass' in remerged[0]['normalization_warnings'], True)
check('later-position merge still keeps counters/cost',
      (remerged[0]['billing_counters']['billable_output_tokens'], remerged[0]['reported_cost_usd']),
      (89, 0.0000087543))
check('later-position merge still retains raw snapshots', len(remerged[0]['raw_provider_usage_snapshots']) >= 2, True)
# control: same record first keeps its incoming warning
control = deduplicate([wrec, row({}, response_id='scratch-dedupe-full')])
check('incoming warnings from first duplicate preserved (order asymmetry)',
      'custom_warning_from_prior_pass' in control[0]['normalization_warnings'], True)

# --- 6. validation matrix ---
alias_cases = [
    ('unequal aliases rejected', lambda: row({'prompt_tokens_details': {'cache_write_tokens': 0, 'cache_creation_tokens': 7}}), 'ReconciliationError'),
    ('reversed unequal aliases rejected', lambda: row({'prompt_tokens_details': {'cache_write_tokens': 7, 'cache_creation_tokens': 0}}), 'ReconciliationError'),
    ('bool alias rejected', lambda: row({'prompt_tokens_details': {'cache_write_tokens': 0, 'cache_creation_tokens': False}}), 'ValueError'),
    ('negative alias rejected', lambda: row({'prompt_tokens_details': {'cache_write_tokens': -1, 'cache_creation_tokens': -1}}), 'ValueError'),
    ('float alias rejected', lambda: row({'prompt_tokens_details': {'cache_write_tokens': 1.5, 'cache_creation_tokens': 1.5}}), 'ValueError'),
    ('list details rejected (not AttributeError)', lambda: row({'completion_tokens_details': []}), 'ValueError'),
    ('string details rejected', lambda: row({'prompt_tokens_details': 'x'}), 'ValueError'),
    ('int details rejected', lambda: row({'completion_tokens_details': 3}), 'ValueError'),
    ('null details -> null counters', 'SPECIAL_NULL', None),
]
for name, fn, exp in alias_cases:
    if fn == 'SPECIAL_NULL':
        r_ = row({'prompt_tokens_details': None, 'completion_tokens_details': None})
        check('null details -> null counters', (r_['billing_counters']['cached_input_tokens'], r_['billing_counters']['cache_write_tokens'], r_['billing_counters']['diagnostic_reasoning_tokens']), (None, None, None))
    else:
        check(name, rejects(fn), exp)
for name, v in [('neg cost -1', -1), ('nan cost', float('nan')), ('inf cost', float('inf')), ('bool cost', True), ('str cost', '0.1')]:
    check(name + ' rejected', rejects(lambda v=v: row({'cost': v})), 'ValueError')
check('zero cost accepted', row({'cost': 0})['reported_cost_usd'], 0)
for name, usage, exp in [
    ('negative counter rejected', {'prompt_tokens': -1}, 'ValueError'),
    ('bool counter rejected', {'completion_tokens': True}, 'ValueError'),
    ('float counter rejected', {'prompt_tokens': 1.0}, 'ValueError'),
    ('nested nan rejected', {'prompt_tokens_details': {'cached_tokens': float('nan')}}, 'ValueError'),
    ('nested negative reasoning rejected', {'completion_tokens_details': {'reasoning_tokens': -2}}, 'ValueError'),
]:
    check(name, rejects(lambda u=usage: row(u)), exp)
for name, ch in [('invented role', {'actor_role': 'invented'}), ('invented phase', {'phase': 'invented'}),
                 ('invented mapping', {'mapping_id': 'invented'}), ('other provider_tag', {'provider_tag': 'other'}),
                 ('other model', {'requested_model': 'openai/gpt-6.1-terra'}), ('empty run_id', {'run_id': ''}),
                 ('blank run_id', {'run_id': '   '}), ('int run_id', {'run_id': 7})]:
    check('metadata rejected: ' + name, rejects(lambda ch=ch: row({}, **ch)), 'ValueError')
for name, u in [('usage list', []), ('usage string', 'x'), ('usage None', None)]:
    check('usage type rejected: ' + name, rejects(lambda u_=u: row(u_)), 'ValueError')
check('nonfinite nested anywhere rejected', rejects(lambda: row({'cost': 0.0, 'prompt_tokens_details': {'cached_tokens': float('inf')}})), 'ValueError')

# --- 7. pathological-input exception-type audit (documented contract: ValueError) ---
overflow = rejects(lambda: row({'cost': 10**400}))
check('huge-int cost escapes ValueError contract (overflow)', overflow, 'OverflowError')
surrogate = rejects(lambda: row({}, run_id='\ud800'))
check('lone-surrogate run_id stays within ValueError contract (UnicodeError subclass)', surrogate, 'UnicodeEncodeError')
import normalize_usage as nu
check('UnicodeEncodeError subclasses ValueError', issubclass(__import__('builtins').UnicodeEncodeError, ValueError), True)
check('missing run_id in deduplicate escapes contract', rejects(lambda: deduplicate([{'source': 'captured_gateway_usage', 'provider_response_id': 'x', 'record_id': 'f' * 64}])), 'KeyError')

# --- 8. schema/output alignment + meta-validation ---
props = set(SCHEMA['properties'])
rec = row(hist_usage, response_id='scratch-align')
check('normalizer output keys == schema properties', set(rec), props)
jsonschema.Draft202012Validator.check_schema(SCHEMA)
print('schema meta-validation OK')
check('mapping registry has exactly the observed mapping', len(__import__('normalize_usage', fromlist=['x']).QUALIFIED_MAPPINGS), 1)

failed = [n for n, ok in results if not ok]
print(f"checks={len(results)} failed={len(failed)}")
if failed:
    print('FAILED:', failed)
sys.exit(1 if failed else 0)
