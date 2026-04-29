"""
VulnScan Backend – Unit Tests
Run with: pytest tests/ -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from rules.engine import RuleEngine
from scanners.xss_scanner import XSSScanner, REFLECTION_SIGNATURES
from scanners.sqli_scanner import SQLiScanner, ERROR_SIGNATURES
from scanners.csrf_scanner import CSRFScanner
from scanners.header_scanner import HeaderScanner


# ── Rule Engine tests ────────────────────────────────────────

class TestRuleEngine:
    def setup_method(self):
        self.engine = RuleEngine()

    def test_xss_finding_enriched(self):
        raw = {
            'type': 'xss', 'subtype': 'reflected',
            'url': 'http://test.com?q=1', 'parameter': 'q',
            'payload': '<script>alert(1)</script>',
            'evidence': '...<script>alert(1)</script>...',
        }
        result = self.engine.evaluate(raw)
        assert result is not None
        assert result['name'] == 'Cross-Site Scripting (XSS)'
        assert result['severity'] == 'high'
        assert result['owasp'] == 'A03:2021 – Injection'
        assert result['cwe'] == 'CWE-79'
        assert 'id' in result
        assert 'remediation' in result
        assert len(result['remediation']) > 0

    def test_sqli_finding_enriched(self):
        raw = {
            'type': 'sqli', 'subtype': 'error_based',
            'url': 'http://test.com/search?q=1', 'parameter': 'q',
            'payload': "'", 'evidence': "SQL syntax error",
        }
        result = self.engine.evaluate(raw)
        assert result is not None
        assert result['severity'] == 'critical'
        assert result['cwe'] == 'CWE-89'

    def test_time_based_sqli_severity_is_high(self):
        raw = {
            'type': 'sqli', 'subtype': 'time_based',
            'url': 'http://test.com/?id=1', 'parameter': 'id',
            'payload': "1' AND SLEEP(3)--",
            'evidence': 'Response delayed 3.1s',
        }
        result = self.engine.evaluate(raw)
        assert result['severity'] == 'high'

    def test_csrf_finding_enriched(self):
        raw = {
            'type': 'csrf', 'subtype': 'missing_token',
            'url': 'http://test.com/contact',
            'evidence': "Form fields: ['name', 'email']",
            'severity_hint': 'medium',
        }
        result = self.engine.evaluate(raw)
        assert result is not None
        assert result['severity'] == 'medium'
        assert result['cwe'] == 'CWE-352'

    def test_unknown_type_returns_none(self):
        raw = {'type': 'unknown_vuln', 'url': 'http://test.com'}
        result = self.engine.evaluate(raw)
        assert result is None

    def test_id_is_deterministic(self):
        raw = {
            'type': 'xss', 'subtype': 'reflected',
            'url': 'http://test.com?q=1', 'parameter': 'q',
            'payload': '<script>', 'evidence': '',
        }
        r1 = self.engine.evaluate(raw)
        r2 = self.engine.evaluate(raw)
        assert r1['id'] == r2['id']

    def test_severity_hint_overrides_default(self):
        raw = {
            'type': 'misconfiguration', 'subtype': 'missing_header',
            'url': 'http://test.com', 'header': 'Strict-Transport-Security',
            'evidence': 'Missing', 'severity_hint': 'high',
        }
        result = self.engine.evaluate(raw)
        assert result['severity'] == 'high'


# ── XSS Scanner tests ────────────────────────────────────────

class TestXSSScanner:
    def test_reflection_detected(self):
        payload = '<script>alert("XSS")</script>'
        body = f'<html>Results for: {payload}</html>'
        assert XSSScanner._is_reflected(payload, body)

    def test_encoded_not_reflected(self):
        payload = '<script>alert(1)</script>'
        body = '<html>Results for: &lt;script&gt;alert(1)&lt;/script&gt;</html>'
        assert not XSSScanner._is_reflected(payload, body)

    def test_svg_payload_reflected(self):
        payload = '<svg onload=alert(1)>'
        body = f'<html>{payload}</html>'
        assert XSSScanner._is_reflected(payload, body)

    def test_evidence_extraction(self):
        payload = '<script>alert(1)</script>'
        body = 'Hello world ' + payload + ' end'
        evidence = XSSScanner._extract_evidence(payload, body)
        assert '...' in evidence
        assert 'script' in evidence.lower()

    def test_all_signatures_present(self):
        assert len(REFLECTION_SIGNATURES) >= 5


# ── SQLi Scanner tests ───────────────────────────────────────

class TestSQLiScanner:
    def test_mysql_error_detected(self):
        body = "You have an error in your SQL syntax near ''"
        assert SQLiScanner._has_sql_error(body)

    def test_sqlite_error_detected(self):
        body = "sqlite3::Exception: near \"OR\": syntax error"
        assert SQLiScanner._has_sql_error(body)

    def test_clean_response_not_flagged(self):
        body = "<html><body>Welcome to the shop</body></html>"
        assert not SQLiScanner._has_sql_error(body)

    def test_error_extraction(self):
        body = "A PHP Error was encountered: You have an error in your SQL syntax"
        evidence = SQLiScanner._extract_error(body)
        assert 'sql' in evidence.lower()

    def test_all_error_signatures_present(self):
        assert len(ERROR_SIGNATURES) >= 10


# ── CSRF Scanner tests ───────────────────────────────────────

class TestCSRFScanner:
    def setup_method(self):
        from unittest.mock import MagicMock
        self.scanner = CSRFScanner(http_client=MagicMock())

    def test_post_form_without_token_flagged(self):
        forms = [{
            'action': 'http://test.com/submit',
            'method': 'POST',
            'fields': [
                {'name': 'username', 'type': 'text', 'value': ''},
                {'name': 'email', 'type': 'email', 'value': ''},
            ],
            'page': 'http://test.com',
        }]
        findings = self.scanner.scan(base_url='http://test.com', forms=forms, urls=[])
        assert len(findings) == 1
        assert findings[0]['type'] == 'csrf'

    def test_post_form_with_csrf_token_safe(self):
        forms = [{
            'action': 'http://test.com/submit',
            'method': 'POST',
            'fields': [
                {'name': 'username', 'type': 'text', 'value': ''},
                {'name': 'csrf_token', 'type': 'hidden', 'value': 'abc123'},
            ],
            'page': 'http://test.com',
        }]
        findings = self.scanner.scan(base_url='http://test.com', forms=forms, urls=[])
        assert len(findings) == 0

    def test_get_form_not_flagged(self):
        forms = [{
            'action': 'http://test.com/search',
            'method': 'GET',
            'fields': [{'name': 'q', 'type': 'text', 'value': ''}],
            'page': 'http://test.com',
        }]
        findings = self.scanner.scan(base_url='http://test.com', forms=forms, urls=[])
        assert len(findings) == 0

    def test_authenticity_token_recognized(self):
        forms = [{
            'action': 'http://test.com/submit',
            'method': 'POST',
            'fields': [
                {'name': 'data', 'type': 'text', 'value': ''},
                {'name': 'authenticity_token', 'type': 'hidden', 'value': 'xyz'},
            ],
            'page': 'http://test.com',
        }]
        findings = self.scanner.scan(base_url='http://test.com', forms=forms, urls=[])
        assert len(findings) == 0


# ── Integration smoke test ───────────────────────────────────

class TestRuleEngineIntegration:
    """Verify all scanner output types pass through the rule engine cleanly."""

    def test_all_vuln_types_produce_valid_findings(self):
        engine = RuleEngine()
        raw_findings = [
            {'type': 'xss',              'subtype': 'reflected',            'url': 'http://t.com', 'parameter': 'q', 'payload': '<script>', 'evidence': ''},
            {'type': 'sqli',             'subtype': 'error_based',          'url': 'http://t.com', 'parameter': 'id', 'payload': "'", 'evidence': 'SQL error'},
            {'type': 'csrf',             'subtype': 'missing_token',        'url': 'http://t.com', 'evidence': 'no token', 'severity_hint': 'medium'},
            {'type': 'misconfiguration', 'subtype': 'missing_header',       'url': 'http://t.com', 'header': 'CSP', 'evidence': 'missing', 'severity_hint': 'high'},
            {'type': 'misconfiguration', 'subtype': 'information_disclosure','url': 'http://t.com', 'header': 'Server', 'evidence': 'Apache'},
            {'type': 'misconfiguration', 'subtype': 'insecure_cookie',      'url': 'http://t.com', 'cookie_name': 'session', 'evidence': 'no HttpOnly', 'severity_hint': 'medium'},
        ]
        for raw in raw_findings:
            result = engine.evaluate(raw)
            assert result is not None, f"No result for {raw['type']}/{raw['subtype']}"
            assert 'id' in result
            assert 'severity' in result
            assert result['severity'] in ('critical', 'high', 'medium', 'low', 'info')
            assert 'remediation' in result
            assert isinstance(result['remediation'], list)
