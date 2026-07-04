"""
Pruebas unitarias para el motor de escaneo (scanner.py).
Cada función de detección se prueba con respuestas HTTP simuladas,
sin realizar peticiones reales a internet.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

from app.scanner import (
    FetchedPage,
    build_vulnerability,
    calculate_risk_score,
    check_csrf,
    check_headers,
    check_info_disclosure,
    check_open_redirect,
    check_reflected_xss,
    check_sqli,
    normalize_url,
    probe_sensitive_files,
    same_origin,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_response(status=200, headers=None, text="", url="http://example.com"):
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status
    resp.headers = headers or {}
    resp.text = text
    resp.url = url
    return resp


def make_page(url="http://example.com", headers=None, body="", status=200):
    resp = make_response(status=status, headers=headers or {}, text=body, url=url)
    return FetchedPage(url=url, response=resp, body=body)


# ---------------------------------------------------------------------------
# normalize_url
# ---------------------------------------------------------------------------

class TestNormalizeUrl:
    def test_strips_fragment(self):
        result = normalize_url("http://example.com/path#section")
        assert "#" not in result

    def test_rejects_ftp(self):
        with pytest.raises(ValueError):
            normalize_url("ftp://example.com")

    def test_rejects_no_scheme(self):
        with pytest.raises(ValueError):
            normalize_url("example.com")

    def test_keeps_query(self):
        result = normalize_url("https://example.com/search?q=test")
        assert "q=test" in result

    def test_https_accepted(self):
        result = normalize_url("https://example.com/")
        assert result.startswith("https://")


# ---------------------------------------------------------------------------
# same_origin
# ---------------------------------------------------------------------------

class TestSameOrigin:
    def test_same_domain(self):
        assert same_origin("http://example.com", "http://example.com/page") is True

    def test_different_domain(self):
        assert same_origin("http://example.com", "http://evil.com") is False

    def test_different_scheme_counts_as_same_netloc(self):
        # same_origin solo compara netloc; http y https con mismo dominio son "mismo origen"
        assert same_origin("http://example.com", "https://example.com") is True

    def test_javascript_rejected(self):
        assert same_origin("http://example.com", "javascript:alert(1)") is False


# ---------------------------------------------------------------------------
# build_vulnerability
# ---------------------------------------------------------------------------

class TestBuildVulnerability:
    def test_structure(self):
        vuln = build_vulnerability("xss", "high", "XSS", "desc", "ev", "fix", "http://x.com", "q")
        assert vuln["module"] == "xss"
        assert vuln["severity"] == "high"
        assert vuln["parameter"] == "q"

    def test_no_parameter(self):
        vuln = build_vulnerability("headers", "low", "T", "d", None, "r", "http://x.com")
        assert vuln["parameter"] is None
        assert vuln["evidence"] is None


# ---------------------------------------------------------------------------
# calculate_risk_score
# ---------------------------------------------------------------------------

class TestCalculateRiskScore:
    def test_empty(self):
        assert calculate_risk_score([]) == 0

    def test_capped_at_100(self):
        vulns = [{"severity": "critical"}] * 10
        assert calculate_risk_score(vulns) == 100

    def test_mixed_severities(self):
        vulns = [{"severity": "high"}, {"severity": "low"}, {"severity": "info"}]
        score = calculate_risk_score(vulns)
        assert score == 25 + 5 + 1

    def test_unknown_severity_counts_as_zero(self):
        vulns = [{"severity": "unknown"}]
        assert calculate_risk_score(vulns) == 0


# ---------------------------------------------------------------------------
# check_headers
# ---------------------------------------------------------------------------

class TestCheckHeaders:
    def test_detects_missing_csp(self):
        page = make_page(headers={})
        vulns = check_headers(page)
        titles = [v["title"] for v in vulns]
        assert "Content-Security-Policy ausente" in titles

    def test_detects_missing_xfo(self):
        page = make_page(headers={})
        vulns = check_headers(page)
        titles = [v["title"] for v in vulns]
        assert "X-Frame-Options ausente" in titles

    def test_no_false_positive_when_headers_present(self):
        headers = {
            "Content-Security-Policy": "default-src 'self'",
            "X-Frame-Options": "DENY",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=()",
            "X-XSS-Protection": "1; mode=block",
        }
        page = make_page(url="http://example.com", headers=headers)
        vulns = [v for v in check_headers(page) if v["title"] != "Strict-Transport-Security ausente"]
        assert vulns == []

    def test_detects_missing_hsts_on_https(self):
        page = make_page(url="https://example.com", headers={})
        vulns = check_headers(page)
        titles = [v["title"] for v in vulns]
        assert "Strict-Transport-Security ausente" in titles

    def test_no_hsts_check_on_http(self):
        page = make_page(url="http://example.com", headers={})
        vulns = check_headers(page)
        titles = [v["title"] for v in vulns]
        assert "Strict-Transport-Security ausente" not in titles


# ---------------------------------------------------------------------------
# check_info_disclosure
# ---------------------------------------------------------------------------

class TestCheckInfoDisclosure:
    def test_detects_server_header(self):
        page = make_page(headers={"server": "Apache/2.4.51"})
        vulns = check_info_disclosure(page)
        assert any("Server" in v["title"] for v in vulns)

    def test_detects_powered_by(self):
        page = make_page(headers={"x-powered-by": "PHP/8.1"})
        vulns = check_info_disclosure(page)
        assert any("X-Powered-By" in v["title"] for v in vulns)

    def test_detects_traceback_in_body(self):
        page = make_page(body="Traceback (most recent call last): ...")
        vulns = check_info_disclosure(page)
        assert any(v["module"] == "info_disclosure" for v in vulns)

    def test_clean_response_no_vulns(self):
        page = make_page(headers={}, body="<html><body>Hello</body></html>")
        vulns = check_info_disclosure(page)
        assert vulns == []


# ---------------------------------------------------------------------------
# check_csrf
# ---------------------------------------------------------------------------

class TestCheckCsrf:
    def test_detects_post_form_without_token(self):
        body = '<form method="POST" action="/login"><input type="text" name="user"></form>'
        page = make_page(body=body)
        vulns = check_csrf(page)
        assert len(vulns) == 1
        assert vulns[0]["module"] == "csrf"

    def test_no_finding_when_csrf_token_present(self):
        body = (
            '<form method="POST">'
            '<input type="hidden" name="csrf_token" value="abc123">'
            '<input type="text" name="user">'
            '</form>'
        )
        page = make_page(body=body)
        vulns = check_csrf(page)
        assert vulns == []

    def test_get_form_ignored(self):
        body = '<form method="GET" action="/search"><input type="text" name="q"></form>'
        page = make_page(body=body)
        vulns = check_csrf(page)
        assert vulns == []

    def test_form_default_method_get_ignored(self):
        body = '<form action="/search"><input type="text" name="q"></form>'
        page = make_page(body=body)
        vulns = check_csrf(page)
        assert vulns == []


# ---------------------------------------------------------------------------
# check_reflected_xss
# ---------------------------------------------------------------------------

class TestCheckReflectedXss:
    def test_detects_reflection(self):
        payload = "<script>alert(1337)</script>"
        url = "http://example.com/search?q=hello"
        page = make_page(url=url)

        reflected_resp = make_response(text=f"<html>{payload}</html>", url=url)
        with patch("app.scanner.requests.Session") as mock_session_cls:
            session = mock_session_cls.return_value
            session.get.return_value = reflected_resp
            vulns = check_reflected_xss(page, timeout=5)

        assert len(vulns) == 1
        assert vulns[0]["module"] == "xss"
        assert vulns[0]["severity"] == "high"

    def test_no_params_returns_empty(self):
        page = make_page(url="http://example.com/page")
        vulns = check_reflected_xss(page, timeout=5)
        assert vulns == []

    def test_no_reflection_no_vuln(self):
        url = "http://example.com/?q=hello"
        page = make_page(url=url)

        clean_resp = make_response(text="<html>safe output</html>", url=url)
        with patch("app.scanner.requests.Session") as mock_session_cls:
            session = mock_session_cls.return_value
            session.get.return_value = clean_resp
            vulns = check_reflected_xss(page, timeout=5)

        assert vulns == []


# ---------------------------------------------------------------------------
# check_sqli
# ---------------------------------------------------------------------------

class TestCheckSqli:
    def test_detects_sql_error(self):
        url = "http://example.com/items?id=1"
        page = make_page(url=url, body="normal content")

        error_resp = make_response(
            text="You have an error in your SQL syntax near...",
            url=url,
        )
        with patch("app.scanner.requests.Session") as mock_session_cls:
            session = mock_session_cls.return_value
            session.get.return_value = error_resp
            vulns = check_sqli(page, timeout=5)

        assert len(vulns) == 1
        assert vulns[0]["module"] == "sqli"
        assert vulns[0]["severity"] == "high"

    def test_no_params_returns_empty(self):
        page = make_page(url="http://example.com/items")
        vulns = check_sqli(page, timeout=5)
        assert vulns == []

    def test_no_sql_error_no_vuln(self):
        url = "http://example.com/?id=1"
        page = make_page(url=url, body="Product list")

        clean_resp = make_response(text="Product list", url=url)
        with patch("app.scanner.requests.Session") as mock_session_cls:
            session = mock_session_cls.return_value
            session.get.return_value = clean_resp
            vulns = check_sqli(page, timeout=5)

        assert vulns == []


# ---------------------------------------------------------------------------
# check_open_redirect
# ---------------------------------------------------------------------------

class TestCheckOpenRedirect:
    def test_detects_open_redirect(self):
        url = "http://example.com/login?redirect=home"
        page = make_page(url=url)

        redir_resp = make_response(
            status=302,
            headers={"location": "https://example.com/evil"},
            url=url,
        )
        with patch("app.scanner.requests.Session") as mock_session_cls:
            session = mock_session_cls.return_value
            session.get.return_value = redir_resp
            vulns = check_open_redirect(page, timeout=5)

        assert len(vulns) == 1
        assert vulns[0]["module"] == "open_redirect"

    def test_non_redirect_param_ignored(self):
        url = "http://example.com/?q=hello"
        page = make_page(url=url)
        with patch("app.scanner.requests.Session") as mock_session_cls:
            session = mock_session_cls.return_value
            session.get.return_value = make_response(status=200)
            vulns = check_open_redirect(page, timeout=5)
        assert vulns == []

    def test_no_params_returns_empty(self):
        page = make_page(url="http://example.com/login")
        vulns = check_open_redirect(page, timeout=5)
        assert vulns == []


# ---------------------------------------------------------------------------
# probe_sensitive_files
# ---------------------------------------------------------------------------

class TestProbeSensitiveFiles:
    def test_detects_exposed_env(self):
        env_resp = make_response(
            status=200,
            text="DB_PASSWORD=secret\nAPP_KEY=abc123",
            url="http://example.com/.env",
        )
        not_found = make_response(status=404)

        with patch("app.scanner.requests.Session") as mock_session_cls:
            session = mock_session_cls.return_value
            session.get.side_effect = [env_resp, not_found, not_found]
            vulns = probe_sensitive_files("http://example.com", timeout=5)

        assert any(v["title"] == "Archivo .env expuesto" for v in vulns)
        assert any(v["severity"] == "critical" for v in vulns)

    def test_detects_phpinfo(self):
        phpinfo_resp = make_response(
            status=200,
            text="PHP Version 8.1 phpinfo()",
            url="http://example.com/phpinfo.php",
        )
        not_found = make_response(status=404)

        with patch("app.scanner.requests.Session") as mock_session_cls:
            session = mock_session_cls.return_value
            session.get.side_effect = [not_found, phpinfo_resp, not_found]
            vulns = probe_sensitive_files("http://example.com", timeout=5)

        assert any(v["title"] == "phpinfo expuesto" for v in vulns)

    def test_all_404_no_vulns(self):
        not_found = make_response(status=404)

        with patch("app.scanner.requests.Session") as mock_session_cls:
            session = mock_session_cls.return_value
            session.get.return_value = not_found
            vulns = probe_sensitive_files("http://example.com", timeout=5)

        assert vulns == []
