"""Fail closed before preparation dispatch if any cohort API exhaustion was seen.

This does not set a budget or change providers. It propagates actual controller
exhaustion evidence across otherwise independent preparation branches.
"""
import argparse
import datetime
import json
import hashlib
from pathlib import Path

def check_admission(base, cohort_id):
    base=Path(base).resolve()
    if Path(cohort_id).name!=cohort_id or not cohort_id.startswith('clean-'):
        raise ValueError('Expected a single clean cohort directory name')
    cohort=base/cohort_id
    if not cohort.is_dir():raise ValueError('Cohort directory missing')
    if (base/'STOP_ADMISSION.json').exists():
        return {'allowed':False,'reason':'existing_global_stop','evidence':'STOP_ADMISSION.json'}
    acknowledgments = {}
    resume = cohort/'budget-resumptions.json'
    if resume.exists():
        records = json.loads(resume.read_text())['resumptions']
        for record in records:
            if record.get('user_authorized_resume') is not True or record.get('verified_remaining_usd', 0) <= 0:
                raise ValueError('Invalid budget resumption acknowledgment')
            acknowledgments.update(record['acknowledged_evidence_sha256'])
    def acknowledged(path):
        return acknowledgments.get(str(path.relative_to(base))) == hashlib.sha256(path.read_bytes()).hexdigest()
    evidence=None
    for path in sorted(base.glob(cohort_id+'-*/budget-exhaustion.json')):
        if json.loads(path.read_text()).get('observed') is True and not acknowledged(path):
            evidence=str(path.relative_to(base));break
    if evidence is None:
        for path in sorted(cohort.glob('*/manifest.json')):
            d=json.loads(path.read_text())
            if any(r.get('api_budget_exhausted') is True for r in d.get('roles',[])) and not acknowledged(path):
                evidence=str(path.relative_to(base));break
    if evidence is not None:
        report={'allowed':False,'reason':'actual_api_budget_exhaustion','evidence':evidence,'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'setting_changed':False}
        try:
            with (base/'STOP_ADMISSION.json').open('x') as out:out.write(json.dumps(report,indent=2)+'\n')
        except FileExistsError:pass
        return report
    return {'allowed':True,'cohort_id':cohort_id,'reason':'no_global_stop_or_recorded_cohort_exhaustion','setting_changed':False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--private-root',required=True,type=Path)
    p.add_argument('--cohort-id',required=True)
    args=p.parse_args()
    result=check_admission(args.private_root,args.cohort_id)
    print(json.dumps(result))
    if not result['allowed']:raise SystemExit(1)

if __name__=='__main__':main()
