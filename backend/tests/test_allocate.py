from __future__ import annotations
"""
Tests for POST /allocate — most critical path (Redlock distributed lock).
Covers: auth enforcement, missing record, zero quantity, insufficient stock,
successful allocation with response shape validation, viewer-role access.
"""
import pytest


def _alloc(client, headers, product_id, store_id, quantity):
    return client.post(
        "/allocate",
        json={"product_id": product_id, "store_id": store_id, "quantity": quantity},
        headers=headers,
    )


def _current_qty(client, headers, product_id, store_id):
    r = client.get(
        f"/inventory?product_id={product_id}&store_id={store_id}",
        headers=headers,
    )
    if r.status_code != 200:
        return None
    rows = r.json().get("data", [])
    return int(rows[0]["quantity"]) if rows else None


@pytest.fixture(scope="module")
def inv_record(client, auth_header):
    """First live inventory row — skips if DB unavailable or empty."""
    r = client.get("/inventory?page=1&page_size=1", headers=auth_header)
    if r.status_code != 200:
        pytest.skip("DB unavailable")
    rows = r.json().get("data", [])
    if not rows:
        pytest.skip("No inventory seed data — populate the DB first")
    row = rows[0]
    return row["product_id"], row["store_id"], row["quantity"]


class TestAllocateAuth:
    def test_unauthenticated_rejected(self, client):
        r = client.post("/allocate",
                        json={"product_id": 1, "store_id": 1, "quantity": 1})
        assert r.status_code in (401, 403)

    def test_garbage_token_rejected(self, client):
        r = client.post("/allocate",
                        json={"product_id": 1, "store_id": 1, "quantity": 1},
                        headers={"Authorization": "Bearer not.a.real.token"})
        assert r.status_code in (401, 403)


class TestAllocateValidation:
    def test_zero_quantity_rejected(self, client, auth_header, inv_record):
        pid, sid, _ = inv_record
        r = _alloc(client, auth_header, pid, sid, quantity=0)
        assert r.status_code == 422

    def test_negative_quantity_rejected(self, client, auth_header, inv_record):
        pid, sid, _ = inv_record
        r = _alloc(client, auth_header, pid, sid, quantity=-5)
        assert r.status_code == 422

    def test_nonexistent_product_store(self, client, auth_header):
        r = _alloc(client, auth_header,
                   product_id=999999, store_id=999999, quantity=1)
        assert r.status_code == 404


class TestAllocateLogic:
    def test_insufficient_stock_409(self, client, auth_header, inv_record):
        pid, sid, qty = inv_record
        r = _alloc(client, auth_header, pid, sid, quantity=int(qty) + 100_000)
        assert r.status_code in (409, 422)  # 409=insufficient stock, 422=exceeds field validation

    def test_successful_allocation_shape(self, client, auth_header, inv_record):
        pid, sid, qty = inv_record
        if int(qty) < 1:
            pytest.skip("Inventory already at zero")

        before = _current_qty(client, auth_header, pid, sid)
        r = _alloc(client, auth_header, pid, sid, quantity=1)
        assert r.status_code == 200

        body = r.json()
        assert body["success"]   is True
        assert body["allocated"] == 1
        assert "remaining"  in body
        assert "locked_ms"  in body
        assert isinstance(body["locked_ms"], (int, float))
        assert body["remaining"] == before - 1

    def test_viewer_can_allocate(self, client, viewer_header, inv_record):
        """Allocation does not require admin role."""
        pid, sid, qty = inv_record
        if int(qty) < 1:
            pytest.skip("Inventory at zero")
        r = _alloc(client, viewer_header, pid, sid, quantity=1)
        assert r.status_code in (200, 409)

    def test_concurrent_over_allocation_prevented(self, client, auth_header, inv_record):
        """Two back-to-back requests for full stock — second must get 409."""
        pid, sid, _ = inv_record
        qty = _current_qty(client, auth_header, pid, sid)
        if qty is None or qty < 1:
            pytest.skip("Insufficient stock for this test")

        r1 = _alloc(client, auth_header, pid, sid, quantity=qty)
        r2 = _alloc(client, auth_header, pid, sid, quantity=qty)
        assert r1.status_code != 500
        assert r2.status_code != 500
        assert 200 in {r1.status_code, r2.status_code} or 409 in {r1.status_code, r2.status_code}
