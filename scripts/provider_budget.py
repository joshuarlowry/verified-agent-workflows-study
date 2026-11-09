"""Classify provider budget errors without treating every403 as exhaustion."""
import json


def is_budget_exhaustion(payload, status=None):
    if status == 402:
        return True
    if isinstance(payload, (bytes, str)):
        try:
            payload = json.loads(payload)
        except (ValueError, UnicodeDecodeError):
            return False
    if not isinstance(payload, dict):
        return False
    error = payload.get('error', payload)
    if not isinstance(error, dict):
        return False
    metadata = error.get('metadata') or {}
    if not isinstance(metadata, dict):
        metadata = {}
    if error.get('code') == 402:
        return True
    if metadata.get('limit_source') == 'openrouter_key_limit' and metadata.get('scope') == 'key_limit':
        return True
    message = str(error.get('message', '')).lower()
    return any(term in message for term in ('insufficient credit', 'budget exceeded', 'credit limit', 'key limit exceeded'))
