
from __future__ import annotations
import os, base64, json, pytest

_ADMIN  = os.environ.get("ADMIN_PASSWORD",  "test-admin-ci")
_VIEWER = os.environ.get("VIEWER_PASSWORD", "test-viewer-ci")


def test_admin_login_success(client):
    r = client.post("/auth/token", json={"username": "admin", "password": _ADMIN})
    assert r.status_code == 200
    d = r.json()
    assert "access_token" in d
    assert d["token_type"] == "bearer"


def test_viewer_login_success(client):
    r = client.post("/auth/token", json={"username": "viewer", "password": _VIEWER})
    assert r.status_code == 200


def test_wrong_password_401(client):
    r = client.post("/auth/token", json={"username": "admin", "password": "wrong"})
    assert r.status_code == 401
    assert r.json()["detail"] == "Invalid credentials"


def test_unknown_user_401(client):
    r = client.post("/auth/token", json={"username": "ghost", "password": "x"})
    assert r.status_code == 401


def test_empty_password_422(client):
    r = client.post("/auth/token", json={"username": "admin", "password": ""})
    assert r.status_code == 422


def test_empty_username_422(client):
    r = client.post("/auth/token", json={"username": "", "password": "x"})
    assert r.status_code == 422


def test_oversized_password_422(client):
    r = client.post("/auth/token", json={"username": "admin", "password": "x" * 129})
    assert r.status_code == 422


def test_sql_injection_rejected(client):
    for payload in ["admin'--", "' OR '1'='1"]:
        r = client.post("/auth/token", json={"username": payload, "password": "x"})
        assert r.status_code in (401, 422)


def test_health_no_auth(client):
    r = client.get("/health")
    assert r.status_code == 200


def test_protected_no_token_403(client):
    r = client.get("/products")
    assert r.status_code == 403


def test_protected_garbage_token_401(client):
    r = client.get("/products", headers={"Authorization": "Bearer not.a.jwt"})
    assert r.status_code == 401


def test_token_payload_has_correct_role(client):
    r = client.post("/auth/token", json={"username": "admin", "password": _ADMIN})
    assert r.status_code == 200
    tok = r.json()["access_token"]
    pad     = 4 - len(tok.split(".")[1]) % 4
    payload = json.loads(base64.urlsafe_b64decode(tok.split(".")[1] + "=" * pad))
    assert payload["role"] == "admin"
    assert payload["sub"]  == "admin"
    assert "exp" in payload


def test_viewer_cannot_create_product(client, viewer_header):
    r = client.post("/products", json={
        "sku": "V-SKU", "name": "T", "category": "T",
        "unit_cost": "10.00", "unit_price": "20.00",
    }, headers=viewer_header)
    assert r.status_code == 403
