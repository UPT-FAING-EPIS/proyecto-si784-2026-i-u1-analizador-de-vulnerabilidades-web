import uuid
import socket

import pytest


def _mysql_available() -> bool:
    try:
        sock = socket.create_connection(("127.0.0.1", 3306), timeout=1)
        sock.close()
        return True
    except OSError:
        return False


requires_db = pytest.mark.skipif(
    not _mysql_available(),
    reason="MySQL no disponible localmente — este test corre en CI con el servicio MySQL",
)


def unique_email() -> str:
    return f"ci-{uuid.uuid4().hex[:10]}@example.com"


def register(client, email, password="TestPassword123", username=None):
    username = username or email.split("@")[0]
    return client.post(
        "/api/auth/register",
        json={"email": email, "username": username, "password": password},
    )


@requires_db
def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


@requires_db
def test_register_and_login(client):
    email = unique_email()
    res = register(client, email)
    assert res.status_code == 201
    body = res.json()
    assert body["user"]["email"] == email
    assert body["access_token"]

    login_res = client.post(
        "/api/auth/login",
        data={"username": email, "password": "TestPassword123"},
    )
    assert login_res.status_code == 200
    assert login_res.json()["access_token"]


@requires_db
def test_register_duplicate_email_conflict(client):
    email = unique_email()
    assert register(client, email).status_code == 201
    assert register(client, email).status_code == 409


@requires_db
def test_scan_lifecycle_via_jwt(client):
    email = unique_email()
    token = register(client, email).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    create_res = client.post(
        "/api/scans",
        json={"target_url": "http://example.com", "depth": 1},
        headers=headers,
    )
    assert create_res.status_code == 201
    scan = create_res.json()

    detail_res = client.get(f"/api/scans/{scan['id']}", headers=headers)
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["status"] == "completed"
    assert detail["vulnerability_count"] == 1
    assert detail["vulnerabilities"][0]["title"] == "Content-Security-Policy ausente"


@requires_db
def test_scan_requires_auth(client):
    res = client.post("/api/scans", json={"target_url": "http://example.com"})
    assert res.status_code == 401


@requires_db
def test_api_key_flow_integrations(client):
    email = unique_email()
    token = register(client, email).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    key_res = client.post("/api/api-keys", json={"name": "ci-test-key"}, headers=headers)
    assert key_res.status_code == 201
    api_key = key_res.json()["api_key"]

    me_res = client.get("/api/integrations/me", headers={"X-API-Key": api_key})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email

    scan_res = client.post(
        "/api/integrations/scans",
        json={"target_url": "http://example.com", "depth": 1},
        headers={"X-API-Key": api_key},
    )
    assert scan_res.status_code == 201
    scan_id = scan_res.json()["id"]

    detail_res = client.get(
        f"/api/integrations/scans/{scan_id}", headers={"X-API-Key": api_key}
    )
    assert detail_res.status_code == 200
    assert detail_res.json()["status"] == "completed"


@requires_db
def test_integrations_require_api_key(client):
    res = client.get("/api/integrations/me")
    assert res.status_code == 401
