import os
import socket
from unittest.mock import patch

os.environ.setdefault("DB_HOST", "127.0.0.1")
os.environ.setdefault("DB_PORT", "3306")
os.environ.setdefault("DB_USER", "root")
os.environ.setdefault("DB_PASSWORD", "root")
os.environ.setdefault("DB_NAME", "web_vulnerability_scanner_test")
os.environ.setdefault("SECRET_KEY", "ci-test-secret-key")
os.environ.setdefault("FRONTEND_ORIGIN", "http://localhost:3000")

import pytest
from fastapi.testclient import TestClient

from app.main import app



FAKE_VULNERABILITIES = [
    {
        "module": "headers",
        "severity": "medium",
        "title": "Content-Security-Policy ausente",
        "description": "Hallazgo simulado para pruebas de CI.",
        "evidence": None,
        "remediation": "Definir una politica CSP.",
        "url": "http://example.com",
        "parameter": None,
    }
]


@pytest.fixture()
def client():
    # No hacemos peticiones HTTP reales durante los tests: se simula el motor de
    # escaneo para que el pipeline de CI sea rapido y no dependa de internet.
    with patch("app.main.scan_target", return_value=(FAKE_VULNERABILITIES, 42)):
        with TestClient(app) as test_client:
            yield test_client
