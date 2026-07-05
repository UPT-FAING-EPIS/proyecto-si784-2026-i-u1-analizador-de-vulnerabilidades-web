"""
Steps BDD para deteccion de vulnerabilidades (features/scanner.feature)
"""
from __future__ import annotations

import sys
import os
from unittest.mock import MagicMock, patch

import pytest
import requests as req_lib
from pytest_bdd import given, scenarios, then, when

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from scanner import check_headers, detect_technologies, inject_param, vuln

scenarios("../features/scanner.feature")


def _mock_resp(headers=None, text="", url="http://example.com"):
    resp = MagicMock(spec=req_lib.Response)
    resp.status_code = 200
    resp.headers = headers or {}
    resp.text = text
    resp.url = url
    resp.cookies = []
    return resp


@pytest.fixture
def ctx():
    return {}


# ── GIVENs ────────────────────────────────────────────────────

@given("un sitio sin cabeceras de seguridad configuradas")
def site_no_headers(ctx):
    ctx["mock_resp"] = _mock_resp(headers={})
    ctx["url"] = "http://example.com"


@given("un sitio con todas las cabeceras de seguridad configuradas")
def site_all_headers(ctx):
    ctx["mock_resp"] = _mock_resp(headers={
        "X-Frame-Options": "DENY",
        "Content-Security-Policy": "default-src 'self'",
        "Strict-Transport-Security": "max-age=31536000",
        "X-Content-Type-Options": "nosniff",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "camera=()",
    })
    ctx["url"] = "http://example.com"


@given("un sitio con CORS configurado como wildcard")
def site_cors_wildcard(ctx):
    ctx["mock_resp"] = _mock_resp(headers={"Access-Control-Allow-Origin": "*"})
    ctx["url"] = "http://example.com"


@given("un sitio que no responde")
def site_no_response(ctx):
    ctx["mock_resp"] = None
    ctx["url"] = "http://example.com"


@given("un sitio que usa WordPress")
def site_wordpress(ctx):
    ctx["mock_resp"] = _mock_resp(text="<html><link href='/wp-content/themes/x.css'></html>")
    ctx["url"] = "http://example.com"


@given("un hallazgo de tipo sqli con severidad high")
def finding_sqli(ctx):
    ctx["finding"] = vuln("sqli", "high", "SQL Injection detectado", "Desc", "http://x.com")


@given("un hallazgo con evidencia de 600 caracteres")
def finding_long_evidence(ctx):
    ctx["finding"] = vuln("xss", "high", "XSS", "Desc", "http://x.com", evidence="e" * 600)


@given("una URL con parametros de consulta")
def url_with_params(ctx):
    ctx["url_param"] = "http://example.com/search?q=hello&page=1"


@given("una URL sin parametros de consulta")
def url_no_params(ctx):
    ctx["url_param"] = "http://example.com/items"


# ── WHENs ─────────────────────────────────────────────────────

@when("analizo las cabeceras del sitio")
def when_check_headers(ctx):
    with patch("scanner.safe_get", return_value=ctx["mock_resp"]):
        ctx["findings"] = check_headers(ctx["url"])


@when("detecto las tecnologias del sitio")
def when_detect_tech(ctx):
    with patch("scanner.safe_get", return_value=ctx["mock_resp"]):
        ctx["tech"] = detect_technologies(ctx["url"])


@when("verifico la estructura del hallazgo")
def when_verify_finding(ctx):
    pass  # el hallazgo ya está en ctx["finding"]


@when("inyecto un payload en los parametros")
def when_inject(ctx):
    ctx["injected"] = inject_param(ctx["url_param"], "PAYLOAD")


# ── THENs ─────────────────────────────────────────────────────

@then("debo encontrar al menos una vulnerabilidad de cabecera faltante")
def then_has_header_vuln(ctx):
    found = [f for f in ctx["findings"] if f["vuln_type"] == "Missing Security Header"]
    assert len(found) >= 1, f"Se esperaba >= 1 hallazgo de cabecera, se encontraron {len(found)}"


@then("no debo encontrar vulnerabilidades de cabecera faltante")
def then_no_header_vuln(ctx):
    found = [f for f in ctx["findings"] if f["vuln_type"] == "Missing Security Header"]
    assert found == [], f"Se esperaban 0 hallazgos de cabecera, se encontraron: {found}"


@then("debo encontrar una vulnerabilidad de tipo CORS Misconfiguration")
def then_cors_vuln(ctx):
    found = [f for f in ctx["findings"] if f["vuln_type"] == "CORS Misconfiguration"]
    assert len(found) >= 1


@then("debo obtener una lista de hallazgos vacia")
def then_empty_findings(ctx):
    assert ctx["findings"] == []


@then("WordPress debe estar en la lista de CMS detectados")
def then_wordpress_detected(ctx):
    assert "WordPress" in ctx["tech"]["cms"]


@then("la lista de CMS detectados debe estar vacia")
def then_empty_cms(ctx):
    assert ctx["tech"]["cms"] == []


@then("el tipo de vulnerabilidad debe ser sqli")
def then_type_sqli(ctx):
    assert ctx["finding"]["vuln_type"] == "sqli"


@then("la severidad debe ser high")
def then_severity_high(ctx):
    assert ctx["finding"]["severity"] == "high"


@then("la evidencia debe tener exactamente 500 caracteres")
def then_evidence_500(ctx):
    assert len(ctx["finding"]["evidence"]) == 500


@then("el payload debe aparecer en la URL resultante")
def then_payload_in_url(ctx):
    assert "PAYLOAD" in ctx["injected"]


@then("la URL resultante debe contener parametros con el payload")
def then_params_added(ctx):
    assert "PAYLOAD" in ctx["injected"]
    assert "=" in ctx["injected"]
