import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from preparation_admission import check_admission


class ResumeAdmission(unittest.TestCase):
    def test_resume_acknowledges_only_exact_historical_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            cohort = base/'clean-test'
            cohort.mkdir()
            run = base/'clean-test-first'
            run.mkdir()
            evidence = run/'budget-exhaustion.json'
            evidence.write_text('{"observed":true}')
            self.assertFalse(check_admission(base, cohort.name)['allowed'])
            stop = base/'STOP_ADMISSION.json'
            stop.rename(base/'archived-stop.json')
            record = {'user_authorized_resume': True, 'verified_remaining_usd': 10,
                      'acknowledged_evidence_sha256': {str(evidence.relative_to(base)): hashlib.sha256(evidence.read_bytes()).hexdigest()}}
            (cohort/'budget-resumptions.json').write_text(json.dumps({'resumptions': [record]}))
            self.assertTrue(check_admission(base, cohort.name)['allowed'])
            stop.write_text('{}')
            self.assertFalse(check_admission(base, cohort.name)['allowed'])
            stop.unlink()
            evidence.write_text('{"observed":true,"new":"changed"}')
            self.assertFalse(check_admission(base, cohort.name)['allowed'])
            stop.unlink()
            evidence.write_text('{"observed":true}')
            new_run = base/'clean-test-second'
            new_run.mkdir()
            (new_run/'budget-exhaustion.json').write_text('{"observed":true}')
            self.assertFalse(check_admission(base, cohort.name)['allowed'])


if __name__ == '__main__':
    unittest.main()
