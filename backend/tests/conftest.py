from __future__ import annotations
import os, pytest
from fastapi.testclient import TestClient

# ── environment must be set before any app import ────────────────────
os.environ.setdefault("DB_HOST",          "localhost")
os.environ.setdefault("DB_PORT",          "5432")
os.environ.setdefault("DB_NAME",          "retail_db")
os.environ.setdefault("DB_USER",          "postgres")
os.environ.setdefault("DB_PASS",          os.getenv("DB_PASS", "niveditha"))
os.environ.setdefault("REDIS_HOST",       "localhost")
os.environ.setdefault("REDIS_PORT",       "6379")
os.environ.setdefault("JWT_SECRET",       "test-secret-key-exactly-32-chars-ok")
os.environ.setdefault("JWT_ALGORITHM",    "HS256")
os.environ.setdefault("ADMIN_PASSWORD",   os.getenv("ADMIN_PASSWORD", "test-admin-ci"))
os.environ.setdefault("VIEWER_PASSWORD",  os.getenv("VIEWER_PASSWORD", "test-viewer-ci"))

from backend.app.main import app               # noqa: E402
from backend.app.core.security import create_token  # noqa: E402
from backend.app.core.database import execute_query, execute_write  # noqa: E402


def _seed_db():
    """Insert minimum test data so tests never skip due to empty DB."""
    try:
        # Check if already seeded
        rows = execute_query("SELECT COUNT(*) as c FROM products")
        if rows and rows[0]["c"] >= 1:
            return  # already seeded

        execute_write("""
            INSERT INTO stores (name, location)
            VALUES ('Test Store', 'Test City')
            ON CONFLICT (name) DO NOTHING
        """)
        execute_write("""
            INSERT INTO products (name, category, price, cost, sku)
            VALUES ('Test Product', 'Electronics', 999.00, 500.00, 'TEST-001')
            ON CONFLICT (sku) DO NOTHING
        """)
        execute_write("""
            INSERT INTO inventory (product_id, store_id, quantity, reorder_point)
            SELECT p.id, s.id, 100, 10
            FROM products p, stores s
            WHERE p.sku = 'TEST-001' AND s.name = 'Test Store'
            ON CONFLICT (product_id, store_id) DO UPDATE SET quantity = 100
        """)
    except Exception as e:
        # DB not available — tests will skip gracefully
        print(f"[conftest] DB seed skipped: {e}")


# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture(scope="session", autouse=True)
def seed_database():
    """Seed DB once per test session."""
    _seed_db()


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
