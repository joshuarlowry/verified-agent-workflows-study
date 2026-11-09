import unittest
from provider_budget import is_budget_exhaustion


class BudgetErrors(unittest.TestCase):
    def test_structured_key_limit(self):
        error = {'error': {'code': 403, 'metadata': {'limit_source': 'openrouter_key_limit', 'scope': 'key_limit'}}}
        self.assertTrue(is_budget_exhaustion(error, 403))
        self.assertTrue(is_budget_exhaustion(error))  # Same payload inside SSE.

    def test_legacy_and_malformed(self):
        self.assertTrue(is_budget_exhaustion(b'not json', 402))
        self.assertTrue(is_budget_exhaustion({'error': {'code': 402}}))
        self.assertTrue(is_budget_exhaustion('{"error":{"message":"Key limit exceeded (total limit)"}}', 403))
        for body in (b'not json', [], None, {'error': None}):
            self.assertFalse(is_budget_exhaustion(body, 502))

    def test_nonbudget_failures(self):
        for code, message in ((403, 'Frozen route policy missing'), (403, 'Authentication failed'), (429, 'Rate limit exceeded'), (504, 'Timed out'), (502, 'HTTPError')):
            self.assertFalse(is_budget_exhaustion({'error': {'code': code, 'message': message}}, code))
        self.assertFalse(is_budget_exhaustion({'error': {'metadata': {'scope': 'key_limit'}}}, 403))


if __name__ == '__main__':
    unittest.main()
