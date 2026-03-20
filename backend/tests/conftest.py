from __future__ import annotations
import os
import sys
import pytest

os.environ.setdefault("JWT_SECRET",        "test-secret-key-exactly-32-chars-ok")
os.environ.setdefault("ADMIN_PASSWORD",    "test-admin-ci")
os.environ.setdefault("VIEWER_PASSWORD",   "test-viewer-ci")
if not os.environ.get("DB_PASS"):
    print("WARNING: DB_PASS not set — DB tests will 500", file=sys.stderr)

from fastapi.testclient import TestClient       # noqa: E402
from backend.app.main import app               # noqa: E402
from backend.app.core.security import create_token  # noqa: E402


@pytest.fixture(scope="session")
def client():
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c

@pytest.fixture(scope="session")
def admin_token():
    return create_token("admin", role="admin")

@pytest.fixture(scope="session")
def viewer_token():
    return create_token("viewer", role="viewer")

@pytest.fixture(scope="session")
def auth_header(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture(scope="session")
def viewer_header(viewer_token):
    return {"Authorization": f"Bearer {viewer_token}"}
