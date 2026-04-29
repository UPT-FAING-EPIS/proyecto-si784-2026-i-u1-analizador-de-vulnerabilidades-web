"""
CSRF Scanner - Detects forms lacking CSRF token protection.
"""

import logging

logger = logging.getLogger(__name__)

CSRF_TOKEN_NAMES = [
    'csrf', 'csrftoken', 'csrf_token', '_token', 'authenticity_token',
    'xsrf', 'xsrf_token', '_csrf', 'nonce', 'form_token',
]


class CSRFScanner:
    def __init__(self, http_client):
        self.http = http_client

    def scan(self, base_url, forms, **_) -> list:
        findings = []

        for form in forms:
            if form['method'] != 'POST':
                continue  # CSRF primarily affects state-changing POST requests

            has_token = any(
                any(tok in f['name'].lower() for tok in CSRF_TOKEN_NAMES)
                for f in form['fields']
            )

            # Also check for hidden token fields
            has_hidden_token = any(
                f['type'] == 'hidden' and any(
                    tok in f['name'].lower() for tok in CSRF_TOKEN_NAMES
                )
                for f in form['fields']
            )

            if not has_token and not has_hidden_token:
                findings.append({
                    'type': 'csrf',
                    'subtype': 'missing_token',
                    'url': form['action'],
                    'description': (
                        f"POST form at '{form['action']}' does not include a CSRF token. "
                        "An attacker can craft a forged request that performs actions on behalf "
                        "of an authenticated user."
                    ),
                    'recommendation': (
                        'Implement synchronizer token pattern: include a unique, '
                        'unpredictable CSRF token in every state-changing form.'
                    ),
                    'evidence': f"Form fields: {[f['name'] for f in form['fields']]}",
                    'severity_hint': 'medium',
                    'page': form.get('page', ''),
                })

        return findings
