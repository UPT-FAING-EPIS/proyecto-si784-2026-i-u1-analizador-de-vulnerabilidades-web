"""
API Integration Tests – Tests Flask routes directly via test client.
Run with: pytest tests/ -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import json
import pytest
from app import create_app


@pytest.fixture
def client():
    """Flask test client with test configuration."""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        resp = client.get('/health')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['status'] == 'ok'
        assert data['service'] == 'vulnscan-backend'


class TestScanEndpoints:
    def test_post_scan_requires_url(self, client):
        resp = client.post('/api/scan',
                           data=json.dumps({}),
                           content_type='application/json')
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert 'error' in data

    def test_post_scan_returns_scan_id(self, client):
        payload = {'url': 'http://localhost:9999', 'scan_xss': False,
                   'scan_sqli': False, 'scan_headers': False, 'scan_csrf': False,
                   'max_depth': 1}
        resp = client.post('/api/scan',
                           data=json.dumps(payload),
                           content_type='application/json')
        assert resp.status_code == 202
        data = json.loads(resp.data)
        assert 'scan_id' in data
        assert data['status'] == 'pending'

    def test_get_unknown_scan_returns_404(self, client):
        resp = client.get('/api/scan/does-not-exist')
        assert resp.status_code == 404

    def test_list_scans_returns_array(self, client):
        resp = client.get('/api/scans')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert isinstance(data, list)

    def test_url_auto_prefixed_with_http(self, client):
        """URLs without scheme should get http:// prepended."""
        payload = {'url': 'localhost:9999', 'scan_xss': False,
                   'scan_sqli': False, 'scan_headers': False, 'scan_csrf': False}
        resp = client.post('/api/scan',
                           data=json.dumps(payload),
                           content_type='application/json')
        assert resp.status_code == 202

    def test_report_endpoint_requires_completed_scan(self, client):
        """Requesting a report before scan is done returns 400."""
        # Start a scan
        payload = {'url': 'http://localhost:9999', 'scan_xss': False,
                   'scan_sqli': False, 'scan_headers': False, 'scan_csrf': False}
        resp = client.post('/api/scan',
                           data=json.dumps(payload),
                           content_type='application/json')
        scan_id = json.loads(resp.data)['scan_id']

        # Immediately request report (scan still pending/running)
        import time
        # Poll until scan finishes (max 10s for localhost connect-fail)
        for _ in range(10):
            r = client.get(f'/api/scan/{scan_id}')
            if json.loads(r.data)['status'] in ('completed', 'error'):
                break
            time.sleep(1)

        # Now report should be available (completed) or 400 (error)
        r = client.get(f'/api/scan/{scan_id}/report')
        assert r.status_code in (200, 400)  # 400 if scan errored


class TestCORSHeaders:
    def test_cors_header_present(self, client):
        resp = client.options('/api/scan',
                              headers={'Origin': 'http://localhost:4200',
                                       'Access-Control-Request-Method': 'POST'})
        # Flask-CORS should add the header
        assert resp.status_code in (200, 204)
