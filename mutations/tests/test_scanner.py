"""
Pruebas unitarias para scanner.py (VulnScan Pro v3).
Todas las funciones se prueban con requests simulados — sin internet.
"""
from __future__ import annotations

import sys
import os
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import requests as req_lib
from scanner import (
    check_headers,
    detect_technologies,
    inject_param,
    safe_get,
    vuln,
)


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def _mock_response(status=200, headers=None, text="", cookies=None, url="http://example.com"):
    resp = MagicMock(spec=req_lib.Response)
    resp.status_code = status
    resp.headers = headers or {}
    resp.text = text
    resp.url = url
    resp.cookies = cookies or []
    return resp


# ──────────────────────────────────────────────────────────────
# vuln() — construcción de hallazgos
# ──────────────────────────────────────────────────────────────

class TestVulnBuilder:
    def test_campos_obligatorios(self):
        v = vuln("sqli", "high", "SQL Injection", "desc", "http://x.com")
        assert v["vuln_type"] == "sqli"
        assert v["severity"] == "high"
        assert v["title"] == "SQL Injection"
        assert v["endpoint"] == "http://x.com"

    def test_evidence_truncada_a_500(self):
        larga = "x" * 600
        v = vuln("xss", "high", "T", "d", "http://x.com", evidence=larga)
        assert len(v["evidence"]) == 500

    def test_evidence_none_queda_vacia(self):
        v = vuln("xss", "high", "T", "d", "http://x.com", evidence=None)
        assert v["evidence"] == ""

    def test_campos_opcionales_por_defecto(self):
        v = vuln("csrf", "medium", "T", "d", "http://x.com")
        assert v["payload"] == ""
        assert v["risk"] == ""
        assert v["solution"] == ""
        assert v["cwe_id"] == ""


# ──────────────────────────────────────────────────────────────
# inject_param()
# ──────────────────────────────────────────────────────────────

class TestInjectParam:
    def test_inyecta_en_parametro_existente(self):
        url = "http://example.com/search?q=hello&page=1"
        result = inject_param(url, "'")
        # La comilla se codifica como %27 en la URL
        assert "hello%27" in result or "hello'" in result
        assert "page=1%27" in result or "page=1'" in result

    def test_sin_params_agrega_id_y_q(self):
        url = "http://example.com/items"
        result = inject_param(url, "PAYLOAD")
        assert "id=PAYLOAD" in result
        assert "q=PAYLOAD" in result

    def test_mantiene_esquema_y_host(self):
        url = "https://mysite.com/path?x=1"
        result = inject_param(url, "test")
        assert result.startswith("https://mysite.com/path")


# ──────────────────────────────────────────────────────────────
# safe_get()
# ──────────────────────────────────────────────────────────────

class TestSafeGet:
    def test_retorna_respuesta_exitosa(self):
        mock_resp = _mock_response(status=200)
        with patch("scanner.requests.get", return_value=mock_resp):
            result = safe_get("http://example.com")
        assert result is not None
        assert result.status_code == 200

    def test_retorna_none_en_excepcion(self):
        with patch("scanner.requests.get", side_effect=req_lib.exceptions.ConnectionError("fallo")):
            result = safe_get("http://example.com")
        assert result is None

    def test_retorna_none_en_timeout(self):
        with patch("scanner.requests.get", side_effect=req_lib.exceptions.Timeout()):
            result = safe_get("http://example.com")
        assert result is None


# ──────────────────────────────────────────────────────────────
# check_headers()
# ──────────────────────────────────────────────────────────────

class TestCheckHeaders:
    def test_detecta_csp_faltante(self):
        resp = _mock_response(headers={})
        with patch("scanner.safe_get", return_value=resp):
            findings = check_headers("http://example.com")
        titles = [f["title"] for f in findings]
        assert any("Content-Security-Policy" in t for t in titles)

    def test_detecta_xframe_faltante(self):
        resp = _mock_response(headers={})
        with patch("scanner.safe_get", return_value=resp):
            findings = check_headers("http://example.com")
        titles = [f["title"] for f in findings]
        assert any("X-Frame-Options" in t for t in titles)

    def test_detecta_hsts_faltante(self):
        resp = _mock_response(headers={})
        with patch("scanner.safe_get", return_value=resp):
            findings = check_headers("http://example.com")
        titles = [f["title"] for f in findings]
        assert any("HSTS" in t or "Strict-Transport-Security" in t for t in titles)

    def test_no_falso_positivo_con_headers_completos(self):
        headers = {
            "X-Frame-Options": "DENY",
            "Content-Security-Policy": "default-src 'self'",
            "Strict-Transport-Security": "max-age=31536000",
            "X-Content-Type-Options": "nosniff",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=()",
        }
        resp = _mock_response(headers=headers)
        with patch("scanner.safe_get", return_value=resp):
            findings = check_headers("http://example.com")
        header_missing = [f for f in findings if f["vuln_type"] == "Missing Security Header"]
        assert header_missing == []

    def test_detecta_cors_wildcard(self):
        headers = {"Access-Control-Allow-Origin": "*"}
        resp = _mock_response(headers=headers)
        with patch("scanner.safe_get", return_value=resp):
            findings = check_headers("http://example.com")
        cors_findings = [f for f in findings if f["vuln_type"] == "CORS Misconfiguration"]
        assert len(cors_findings) >= 1

    def test_detecta_version_servidor_expuesta(self):
        headers = {"server": "Apache/2.4.51 (Ubuntu)"}
        resp = _mock_response(headers=headers)
        with patch("scanner.safe_get", return_value=resp):
            findings = check_headers("http://example.com")
        info_findings = [f for f in findings if "versión" in f["title"].lower() or "Versión" in f["title"]]
        assert len(info_findings) >= 1

    def test_retorna_lista_vacia_si_safe_get_falla(self):
        with patch("scanner.safe_get", return_value=None):
            findings = check_headers("http://example.com")
        assert findings == []

    def test_detecta_x_powered_by(self):
        headers = {"x-powered-by": "PHP/8.1.0"}
        resp = _mock_response(headers=headers)
        with patch("scanner.safe_get", return_value=resp):
            findings = check_headers("http://example.com")
        assert any("X-Powered-By" in f["title"] or "x-powered-by" in f["title"].lower() for f in findings)


# ──────────────────────────────────────────────────────────────
# detect_technologies()
# ──────────────────────────────────────────────────────────────

class TestDetectTechnologies:
    def test_detecta_wordpress(self):
        resp = _mock_response(text="<html><link href='/wp-content/themes/x.css'></html>")
        with patch("scanner.safe_get", return_value=resp):
            tech = detect_technologies("http://example.com")
        assert "WordPress" in tech["cms"]

    def test_detecta_react(self):
        resp = _mock_response(text="<html><script src='/_next/static/chunk.js'></script></html>")
        with patch("scanner.safe_get", return_value=resp):
            tech = detect_technologies("http://example.com")
        assert "Next.js" in tech["libraries"]

    def test_detecta_cloudflare_waf(self):
        resp = _mock_response(
            headers={"cf-ray": "abc123"},
            text="<html>cloudflare</html>"
        )
        with patch("scanner.safe_get", return_value=resp):
            tech = detect_technologies("http://example.com")
        assert "Cloudflare" in tech["waf"] or "Cloudflare" in tech["cdn"]

    def test_retorna_estructura_vacia_sin_respuesta(self):
        with patch("scanner.safe_get", return_value=None):
            tech = detect_technologies("http://example.com")
        assert tech["cms"] == []
        assert tech["frameworks"] == []
        assert tech["libraries"] == []

    def test_detecta_servidor_en_header(self):
        resp = _mock_response(headers={"server": "nginx/1.18.0"})
        with patch("scanner.safe_get", return_value=resp):
            tech = detect_technologies("http://example.com")
        assert "nginx/1.18.0" in tech["server"]
