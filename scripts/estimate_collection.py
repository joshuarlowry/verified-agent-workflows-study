"""Planning-only duration forecast from canonical registration; no observed runtimes."""
import json
import sys
from pathlib import Path


def forecast(r):
    s=r['sample']; f=r['collection_forecast']; lanes=r['execution_schedule']['max_parallel_workflows']
    counts={arm:s['scored_task_count_proposed']*s['core_repetitions_per_task_configuration']+s['calibration_task_count']*s['calibration_repetitions_per_task_configuration'] for arm in r['core_configurations']}
    counts['Gemma alone']+=s['extra_gemma_run_count']; n=sum(counts.values())
    subject=sum(counts[a]*f['mean_subject_minutes_by_system'][a] for a in counts)/60
    overhead=n*f['setup_and_evaluation_minutes_per_run']/60
    worst=n*f['worst_case_subject_minutes_per_run']/60
    cases=[]
    for label,hours in [('Assumed mix',subject+overhead),('All runs hit cutoff',worst+overhead)]:
        for concurrency in sorted({1,lanes}):
            occupied=hours/(concurrency*f['scheduler_utilization_assumption'])
            cases.append({'scenario':label,'lanes':concurrency,'collection_hours':occupied,'days_by_availability':{str(day):occupied/day for day in f['availability_hours_per_day_scenarios']}})
    return {'kind':'planning_assumptions_not_measured','runs':n,'counts_by_arm':counts,'assumed_subject_hours':subject,'setup_evaluation_hours':overhead,'cases':cases,'excludes':f['excludes']}


if __name__=='__main__':
    r=json.loads((Path(__file__).resolve().parents[1]/'registration.json').read_text()); x=forecast(r)
    if '--json' in sys.argv:
        print(json.dumps(x,indent=2))
    else:
        print(f"Planning only: {x['runs']} runs; counts={x['counts_by_arm']}")
        print(f"Assumed subject work {x['assumed_subject_hours']:.2f} h; setup/evaluation work {x['setup_evaluation_hours']:.2f} h")
        for c in x['cases']:
            print(f"{c['scenario']}, {c['lanes']} lane(s): {c['collection_hours']:.2f} collection hours; "+', '.join(f'{days:.2f} days at {day} h/day' for day,days in c['days_by_availability'].items()))
        print('Excludes: '+x['excludes'])
