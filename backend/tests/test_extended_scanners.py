"""
Tests para los módulos scanner extendidos:
  - RedirectScanner
  - InfoDisclosureScanner
  - Integración completa con RuleEngine (todos los tipos)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from unittest.mock import MagicMock, patch
from scanners.redirect_scanner import RedirectScanner, REDIRECT_PARAMS, REDIRECT_PAYLOADS
from scanners.info_disclosure_scanner import (
    InfoDisclosureScanner, SENSITIVE_PATHS, SENSITIVE_PATTERNS,
)
from rules.engine import RuleEngine


# ── RedirectScanner tests ────────────────────────────────────

class TestRedirectScanner:
    def setup_method(self):
        self.http = MagicMock()
        self.scanner = RedirectScanner(self.http)

    def test_open_redirect_detected(self):
        """Un 302 hacia dominio externo debe reportarse."""
        mock_resp = MagicMock()
        mock_resp.status_code = 302
        mock_resp.headers = {'Location': 'https://evil.com/stolen'}
        self.http.session.get.return_value = mock_resp
        self.http.timeout = 10

        urls = ['http://target.com/login?redirect=http://target.com/home']
        findings = self.scanner.scan(base_url='http://target.com', urls=urls, endpoints=[])
        assert len(findings) >= 1
        assert findings[0]['type'] == 'redirect'
        assert findings[0]['subtype'] == 'open_redirect'

    def test_internal_redirect_not_flagged(self):
        """Un 302 al mismo dominio no debe reportarse."""
        mock_resp = MagicMock()
        mock_resp.status_code = 302
        mock_resp.headers = {'Location': 'http://target.com/dashboard'}
        self.http.session.get.return_value = mock_resp
        self.http.timeout = 10

        urls = ['http://target.com/login?redirect=http://target.com/home']
        findings = self.scanner.scan(base_url='http://target.com', urls=urls, endpoints=[])
        assert len(findings) == 0

    def test_non_redirect_param_skipped(self):
        """Parámetros sin nombre de redirección no deben probarse."""
        urls = ['http://target.com/search?q=hello&page=2']
        findings = self.scanner.scan(base_url='http://target.com', urls=urls, endpoints=[])
        # No redirect-related params → http client never called
        assert self.http.session.get.call_count == 0
        assert len(findings) == 0

    def test_200_response_not_flagged(self):
        """Una respuesta 200 (sin redirect) no es Open Redirect."""
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.headers = {}
        self.http.session.get.return_value = mock_resp
        self.http.timeout = 10

        urls = ['http://target.com/go?url=https://target.com/page']
        findings = self.scanner.scan(base_url='http://target.com', urls=urls, endpoints=[])
        assert len(findings) == 0

    def test_common_redirect_params_in_list(self):
        """Lista de parámetros comunes de redirección incluye elementos clave."""
        for param in ('redirect', 'next', 'return', 'url', 'goto'):
            assert param in REDIRECT_PARAMS

    def test_redirect_payloads_include_external_domain(self):
        assert any('evil.com' in p for p in REDIRECT_PAYLOADS)

    def test_connection_error_handled_gracefully(self):
        """Errores de red no deben propagar excepciones."""
        self.http.session.get.side_effect = Exception("Connection refused")
        self.http.timeout = 10
        urls = ['http://target.com/go?redirect=http://target.com/']
        # Should not raise
        findings = self.scanner.scan(base_url='http://target.com', urls=urls, endpoints=[])
        assert isinstance(findings, list)


# ── InfoDisclosureScanner tests ──────────────────────────────

class TestInfoDisclosureScanner:
    def setup_method(self):
        self.http = MagicMock()
        self.scanner = InfoDisclosureScanner(self.http)

    def _make_resp(self, status=200, text='', content_type='text/html'):
        r = MagicMock()
        r.status_code = status
        r.text = text
        r.headers = {'Content-Type': content_type}
        return r

    def test_env_file_detected(self):
        """Un .env accesible debe reportarse como sensitive_file."""
        self.http.get.return_value = self._make_resp(
            text='DB_PASSWORD=supersecret\nAPP_KEY=abc123'
        )
        findings = self.scanner._test_sensitive_paths('http://target.com')
        env_findings = [f for f in findings if '.env' in f['url']]
        assert len(env_findings) >= 1
        assert env_findings[0]['subtype'] == 'sensitive_file'

    def test_404_not_flagged(self):
        """Un 404 en ruta sensible no debe reportarse."""
        self.http.get.return_value = self._make_resp(status=404, text='Not found')
        findings = self.scanner._test_sensitive_paths('http://target.com')
        assert all(f['subtype'] != 'sensitive_file' for f in findings)

    def test_python_traceback_detected(self):
        """Un traceback de Python en la respuesta debe detectarse."""
        body = 'Internal Server Error\nTraceback (most recent call last):\n  File "app.py"'
        self.http.get.return_value = self._make_resp(text=body)
        findings = self.scanner._analyze_response_body('http://target.com/error')
        assert len(findings) >= 1
        assert findings[0]['type'] == 'info_disclosure'

    def test_api_key_in_response_detected(self):
        """Una API key expuesta en el HTML debe detectarse."""
        body = '<html>api_key = "sk-abc123def456ghi789"</html>'
        self.http.get.return_value = self._make_resp(text=body)
        findings = self.scanner._analyze_response_body('http://target.com/')
        assert any('api' in f['description'].lower() or 'key' in f['description'].lower()
                   for f in findings)

    def test_clean_response_not_flagged(self):
        """Una respuesta normal sin datos sensibles no debe reportarse."""
        body = '<html><body><h1>Welcome to our shop</h1><p>Buy our products!</p></body></html>'
        self.http.get.return_value = self._make_resp(text=body)
        findings = self.scanner._analyze_response_body('http://target.com/')
        assert len(findings) == 0

    def test_interesting_403_status_reported(self):
        """Un 403 en ruta sensible debe reportarse como interesante."""
        self.http.get.return_value = self._make_resp(status=403, text='Forbidden')
        findings = self.scanner._test_sensitive_paths('http://target.com')
        forbidden_findings = [f for f in findings if f['subtype'] == 'interesting_status']
        assert len(forbidden_findings) >= 1

    def test_sensitive_paths_list_not_empty(self):
        assert len(SENSITIVE_PATHS) >= 10
        assert '/.env' in SENSITIVE_PATHS
        assert '/.git/config' in SENSITIVE_PATHS

    def test_sensitive_patterns_list_not_empty(self):
        assert len(SENSITIVE_PATTERNS) >= 8

    def test_non_html_response_skipped(self):
        """Respuestas que no son text/* no deben analizarse."""
        self.http.get.return_value = self._make_resp(
            content_type='application/octet-stream', text='binary data'
        )
        findings = self.scanner._analyze_response_body('http://target.com/file.bin')
        assert len(findings) == 0

    def test_looks_like_real_env_content(self):
        assert InfoDisclosureScanner._looks_like_real_content('/.env', 'DB_HOST=localhost')
        assert not InfoDisclosureScanner._looks_like_real_content('/.env', '<html>404 not found</html>')

    def test_looks_like_git_config(self):
        assert InfoDisclosureScanner._looks_like_real_content(
            '/.git/config', '[core]\n\trepositoryformatversion = 0'
        )


# ── Full RuleEngine integration with all scanner types ───────

class TestFullIntegration:
    """End-to-end: todos los tipos de scanner → RuleEngine → hallazgo válido."""

    def setup_method(self):
        self.engine = RuleEngine()

    def _check(self, raw: dict, expected_type: str, expected_min_severity: str = None):
        result = self.engine.evaluate(raw)
        assert result is not None, f"RuleEngine returned None for {raw['type']}"
        assert result['type'] == expected_type
        assert 'id' in result and len(result['id']) > 0
        assert 'remediation' in result and len(result['remediation']) > 0
        assert 'owasp' in result
        assert 'cwe' in result
        assert result['severity'] in ('critical', 'high', 'medium', 'low', 'info')
        return result

    def test_xss_reflected(self):
        r = self._check({
            'type': 'xss', 'subtype': 'reflected',
            'url': 'http://t.com?q=1', 'parameter': 'q',
            'payload': '<script>alert(1)</script>', 'evidence': '...<script>...',
        }, 'xss')
        assert r['severity'] == 'high'

    def test_xss_reflected_form(self):
        r = self._check({
            'type': 'xss', 'subtype': 'reflected_form',
            'url': 'http://t.com/contact', 'parameter': 'name',
            'payload': '"><img src=x onerror=alert(1)>', 'evidence': 'onerror=alert',
        }, 'xss')
        assert r['severity'] == 'high'

    def test_sqli_error_based(self):
        r = self._check({
            'type': 'sqli', 'subtype': 'error_based',
            'url': 'http://t.com/search?q=1', 'parameter': 'q',
            'payload': "'", 'evidence': 'SQL syntax error',
        }, 'sqli')
        assert r['severity'] == 'critical'

    def test_sqli_time_based(self):
        r = self._check({
            'type': 'sqli', 'subtype': 'time_based',
            'url': 'http://t.com/?id=1', 'parameter': 'id',
            'payload': "1' AND SLEEP(3)--", 'evidence': 'Delayed 3.1s',
        }, 'sqli')
        assert r['severity'] == 'high'

    def test_csrf_missing_token(self):
        r = self._check({
            'type': 'csrf', 'subtype': 'missing_token',
            'url': 'http://t.com/submit', 'evidence': "fields: ['email']",
            'severity_hint': 'medium',
        }, 'csrf')
        assert r['severity'] == 'medium'

    def test_misconfiguration_missing_header(self):
        r = self._check({
            'type': 'misconfiguration', 'subtype': 'missing_header',
            'url': 'http://t.com', 'header': 'Content-Security-Policy',
            'evidence': 'header missing', 'severity_hint': 'high',
        }, 'misconfiguration')
        assert r['severity'] == 'high'

    def test_misconfiguration_info_disclosure(self):
        r = self._check({
            'type': 'misconfiguration', 'subtype': 'information_disclosure',
            'url': 'http://t.com', 'header': 'X-Powered-By',
            'evidence': 'X-Powered-By: Flask',
        }, 'misconfiguration')
        assert r['severity'] == 'low'

    def test_misconfiguration_insecure_cookie(self):
        r = self._check({
            'type': 'misconfiguration', 'subtype': 'insecure_cookie',
            'url': 'http://t.com/login', 'cookie_name': 'session',
            'evidence': 'HttpOnly missing', 'severity_hint': 'medium',
        }, 'misconfiguration')
        assert r['severity'] == 'medium'

    def test_redirect_open_redirect(self):
        r = self._check({
            'type': 'redirect', 'subtype': 'open_redirect',
            'url': 'http://t.com/go?next=https://evil.com', 'parameter': 'next',
            'payload': 'https://evil.com', 'evidence': '302 → Location: https://evil.com',
            'severity_hint': 'medium',
        }, 'redirect')
        assert r['severity'] == 'medium'

    def test_info_disclosure_sensitive_file(self):
        r = self._check({
            'type': 'info_disclosure', 'subtype': 'sensitive_file',
            'url': 'http://t.com/.env',
            'evidence': 'HTTP 200 · /.env', 'severity_hint': 'high',
        }, 'info_disclosure')
        assert r['severity'] == 'high'

    def test_info_disclosure_data_in_response(self):
        r = self._check({
            'type': 'info_disclosure', 'subtype': 'sensitive_data_in_response',
            'url': 'http://t.com/error',
            'evidence': 'Traceback (most recent call last):', 'severity_hint': 'medium',
        }, 'info_disclosure')
        assert r['severity'] == 'medium'
