"""Describe frozen C1 first endpoints; no scoring changes, model calls or intervals."""
import argparse
from collections import Counter
import datetime
import hashlib
import json
from pathlib import Path
from zoneinfo import ZoneInfo


def load(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def duration(seconds):
    if seconds is None:
        return "Unknown"
    seconds = round(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}h {minutes:02}m {seconds:02}s" if hours else f"{minutes}m {seconds:02}s"


def build(selection_path):
    selection = load(selection_path)
    slots = selection['ordinary_calibration_slots']
    assert len(slots) == 10 and len({x['run_id'] for x in slots}) == 10
    assert sorted(Counter(x['arm'] for x in slots).values()) == [2] * 5
    assert len(selection['technical_attempts_also_retained']) == 2
    rows = []
    block_provenance = {}
    for slot in slots:
        block = Path(slot['block'])
        grade_path = block / 'grading-first-endpoints/report.json'
        measurement_path = block / 'measurements-final-first-endpoints.json'
        grade = load(grade_path)
        assert grade.get('ended_at_utc'), 'Grading must finish before this report'
        result = next(x for x in grade['rows'] if x['run_id'] == slot['run_id'])
        measurement = next(x for x in load(measurement_path)['rows'] if x['run_id'] == slot['run_id'])
        assert not result.get('error'), 'Report mechanical grading errors explicitly first'
        gates = result['gates']
        assert len(gates) == 13 and set(gates.values()) <= {'pass', 'fail', 'unverified'}
        assert result['accepted'] == all(x == 'pass' for x in gates.values())
        roles = measurement.get('roles')
        prices = [x.get('known_reported_cost_usd_subtotal') for x in roles or []]
        known_cost = sum(x for x in prices if x is not None) if any(x is not None for x in prices) else None
        cost_complete = bool(roles) and len(prices) == len(roles) and all(x is not None for x in prices) and all(x['cost_complete'] for x in roles)
        nonpassing = {key: value for key, value in gates.items() if value != 'pass'}
        if result['accepted']:
            label = 'Pass: all frozen gates'
        elif set(nonpassing) == {'finite_source_preservation'}:
            label = 'Reject: test-preservation policy only'
        elif measurement['endpoint_reason'] == 'infrastructure_failure':
            label = 'No delivery: infrastructure interruption'
        else:
            label = 'Fail: feature acceptance'
        rows.append({
            'run_id': slot['run_id'], 'workflow': slot['arm'], 'repetition': slot['repetition'],
            'position': slot['position'], 'endpoint_reason': measurement['endpoint_reason'],
            'frozen_gate_accepted': result['accepted'], 'display_result': label,
            'gates': gates, 'nonpassing_gates': nonpassing,
            'runtime_seconds': measurement['seconds']['dispatch_to_native_exit'],
            'runtime_definition': 'Native dispatch to process exit; includes tools and waiting, excludes setup and backups.',
            'recorded_provider_cost_usd_subtotal': known_cost, 'recorded_cost_complete': cost_complete,
            'roles': roles, 'unique_worker_requests': measurement['unique_worker_requests'],
            'durable_worker_responses': measurement['durable_worker_responses'],
            'active_human_effort_seconds': measurement['active_human_effort_seconds'],
            'operator_feedback_turns': measurement['operator_feedback_turns'],
            'native_export_capture_revision': 'qualified_regular_file_export' if slot['run_id'] in ['cal-c1-v3-08', 'cal-c1-v3-09', 'cal-c1-v3-10'] else 'original_export_capture',
            'endpoint_receipt_sha256': sha(Path(slot['endpoint_root']) / 'endpoint.json'),
        })
        block_provenance[str(block)] = {'grading_report_sha256': sha(grade_path), 'measurement_report_sha256': sha(measurement_path)}
    return {
        'kind': 'descriptive_C1_calibration_first_endpoint_results',
        'generated_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'scope': 'One calibration task, two repetitions per workflow; not scored study results or independent tasks.',
        'nominal_endpoints': len(rows), 'accepted_by_all_frozen_gates': sum(x['frozen_gate_accepted'] for x in rows),
        'exploratory_timely_all_nonpolicy_gates_pass': sum(all(value == 'pass' for key, value in x['gates'].items() if key != 'finite_source_preservation') for x in rows),
        'scored_runs': 0, 'rows': rows, 'model_calls_for_this_report': 0,
        'selection_sha256': sha(selection_path), 'source_reports': block_provenance,
        'billing_rule': 'Provider-reported known charges once by role; cached input is a subset of input. Reasoning is not added to billed output. Failed-call billing can be unknown.',
        'primary_standardized_pricing': 'Not preregistered for C1: at its first publication no uncached list-price rate card had been frozen. A later prospective card cannot retroactively preregister this comparison. These are observed charge subtotals.',
        'technical_extra_attempts': selection['technical_attempts_also_retained'],
        'limits': [
            'Acceptance is finite machine verification, not semantic completeness or human merge approval.',
            'Both direct Terra patches passed feature/regression/auth/full-app gates; the frozen source rule rejected extra assertions inside an original test. Original grading remains unchanged.',
            'The detailed finite test-edit grammar was not included in the subject public-check bundle or initial prompt. The public FAQ required preserved coverage but did not disclose these structural exclusions. This instrument/contract mismatch limits the validity of all-gate comparisons and must be resolved explicitly before later collection.',
            'One Gemma patch failed the first-workspace zero-count UI requirement; max-failure stopping leaves later feature cases unexecuted.',
            'Both Terra-supervised workflows were interrupted. Their snapshots also fail lint; the full-app command sequence stops at lint, so later app checks were not executed.',
            'Calibration spans disclosed harness repairs. Do not infer a model-only or uniform-harness ranking from this task.',
            'GLM supervisor prompts supplied detailed solution-level SQL and UI directions; Gemma made the edits. The boundary against complete replacement implementations needs explicit reporting, not a hidden new exclusion rule.',
            'One post-endpoint diagnostic exposed terminal worker/supervisor text to the operator; no live feedback followed. A private access disclosure is preserved.',
            'Mechanical operator/harness work and model preparation overhead are outside row charges. Human review effort was not measured; it is not zero.',
            'Earlier acknowledgement and DNS technical attempts remain additional physical attempts and overhead, outside the fixed ten nominal slots.',
            'Only one task is represented. No confidence intervals, cost-per-acceptance ranking or purchasing recommendation are justified here.',
            'The study is AI-managed. The evaluated model families also constructed and cross-reviewed benchmark materials under an explicit independence waiver; this is not an independently authored benchmark.',
        ],
    }


def markdown(report, provider_audit=None):
    eastern = datetime.datetime.fromisoformat(report['generated_at_utc']).astimezone(ZoneInfo('America/New_York')).strftime('%b %d, %Y at %I:%M %p %Z')
    lines = ['# C1 calibration: first verified results', '', f'Published {eastern}. AI-managed study; all original endpoints remain preserved.', '',
             f"**{report['accepted_by_all_frozen_gates']} of 10 runs passed every frozen machine gate.** This is one calibration task, with two repetitions per workflow. No scored study runs have started.", '',
             'All five systems use OpenCode → LiteLLM → OpenRouter. The pinned Gemma route serves BF16; the pinned GLM route serves FP4; Terra uses Azure with high reasoning. Exact dated model IDs and settings remain in [registration.json](../registration.json).', '',
             '| Workflow | Trial | Frozen result | Runtime | Recorded charges |', '|---|---:|---|---:|---:|']
    for row in report['rows']:
        cost = row['recorded_provider_cost_usd_subtotal']
        cost_text = 'Unknown' if cost is None else ('' if row['recorded_cost_complete'] else '≥ ') + f'${cost:.4f}'
        lines.append(f"| {row['workflow']} | {row['repetition']} | {row['display_result']} | {duration(row['runtime_seconds'])} | {cost_text} |")
    lines += ['', 'Runtime includes tools and waits, excluding setup and between-run backups. Charges are provider-reported known subtotals; ≥ means billing is incomplete. They exclude preparation, infrastructure repair, grading and earlier technical attempts. At C1’s first publication, no standardized rate card had been frozen. Revision 21 later froze a [prospective rate card](economic-rate-card.json); any standardized C1 repricing remains post-hoc. These rows remain observed charge subtotals.', '',
              '## What the checks establish', '',
              'The unchanged frozen gates cover 21 public/sealed feature cases, 17 external baseline regression cases, database integrity/schema checks, 31 native authentication probes, full app checks, source/test preservation, timely final return and artifact integrity. A failing sequence can stop early: unexecuted tests are not passes.', '',
              'Both direct Terra runs passed the behavioral, regression, authentication and full-app checks. Their only rejection was the finite original-test rule: new assertions were inserted inside an existing test outside the permitted locations. The original test statements were retained. This is a policy rejection, not an observed functional defect; neither primary result was upgraded after inspection. As an explicitly exploratory diagnostic, seven runs passed every gate except this source policy. That is not a replacement completion definition.', '',
              '**Instrument gap:** the detailed finite test-edit grammar was absent from the public-check bundle and initial subject prompt. The public FAQ required preserved coverage without disclosing these structural exclusions. The five all-gate passes therefore cannot support a fair model-quality ranking. The mismatch must be documented and resolved prospectively, without rewriting C1 results.', '',
              'Gemma trial 1 failed the first-created-workspace zero-count selector check. Both Terra-supervised attempts ended before a supervisor final: provider errors interrupted trial 1; truncated session export interrupted trial 2. Their preserved snapshots also fail lint, so later full-app checks were not executed. The capture repair was separately qualified before the last three unrun slots; no failed actor was retried.', '',
              ]
    if provider_audit is not None:
        assert provider_audit['selection_sha256'] == report['selection_sha256'], 'Provider audit must bind the same fixed selection'
        assert {x['run_id'] for x in provider_audit['rows']} == {x['run_id'] for x in report['rows']}
        def errors(run_id=None, code='429', provider='Crusoe'):
            return sum(group['unique_call_count'] for row in provider_audit['rows'] if run_id is None or row['run_id'] == run_id
                       for role in row['roles'] for group in role['error_groups']
                       if group['body_error_code'] == code and group['body_identified_provider'] == provider)
        assert all(role['failed_call_bodies'] == 0 for row in provider_audit['rows'] for role in row['roles']
                   if not any('google/gemma-4-31b-it' == model for model in role['requested_models']))
        lines += ['## Provider-error attribution', '',
                  f"A subsequent role-by-role audit of all ten fixed C1 endpoints found {errors()} captured response bodies identifying **Crusoe rate limits on Gemma requests**, plus {errors(code='504', provider=None)} worker-route timeout error bodies without provider metadata. No provider error body was captured on the direct GLM, direct Terra or supervisor routes. This is capture evidence, not a guarantee of platform uptime.", '',
                  f"The first failed Terra-supervised run contains **{errors('cal-c1-v3-05')} Gemma/Crusoe rate-limit errors and {errors('cal-c1-v3-05', '504', None)} worker-route timeouts**. The second contains **{errors('cal-c1-v3-07')} Gemma/Crusoe rate-limit errors**, in addition to the separately documented session-export endpoint failure. Those interruptions and retry delays must not be attributed solely to Terra’s coding or supervision capability. Direct Gemma and GLM-supervised runs also encountered rate limits. Workloads and retry bursts differ, so these counts are not independent reliability trials or a causal supervisor comparison. Failed-call billing remains unknown; original timings, endpoints, source and acceptance results are unchanged. [Full fixed-run/role audit and evidence hashes](c1-provider-failure-attribution.json).", '']
    lines += ['## Interpretation and remaining gaps', '']
    lines += ['- ' + text for text in report['limits'] if not text.startswith(('Both direct Terra', 'One Gemma', 'Both Terra-supervised'))]
    lines += ['', 'There are 30 remaining calibration slots before the planned 165 scored generations; their task packets still require qualification. Advancement depends on the registered integrity/readiness gates, not which workflow looks favorable here.', '',
              '[Machine-readable results, role usage and evidence hashes](c1-first-results.json) · [Export-capture repair](c1-export-capture-repair-qualification.json) · [Session-export failure](c1-session-export-failure.json) · [Provider failure](c1-terra-supervised-provider-failure.json)', '']
    lines += ['', '[Preserved application source branches and endpoint hashes](c1-source-endpoints.json). All ten nominal snapshots and the additional DNS-interrupted snapshot are published as separate branches; the study main branch is unchanged by those application commits.', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--selection', required=True, type=Path)
    parser.add_argument('--output-dir', required=True, type=Path)
    parser.add_argument('--provider-attribution', type=Path, help='Optional follow-up raw-provider audit bound to the same fixed selection')
    args = parser.parse_args()
    report = build(args.selection)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, content in [('c1-first-results.json', json.dumps(report, indent=2, allow_nan=False) + '\n'), ('C1_RESULTS.md', markdown(report, load(args.provider_attribution) if args.provider_attribution else None))]:
        with (args.output_dir / name).open('x') as stream:
            stream.write(content)
    print(json.dumps({'nominal': len(report['rows']), 'accepted': report['accepted_by_all_frozen_gates'], 'model_calls': 0}))
