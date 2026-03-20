from __future__ import annotations
"""Tests for GET /shipments and POST /shipments."""
import pytest


class TestListShipments:
    def test_returns_list(self, client, auth_header):
        r = client.get("/shipments", headers=auth_header)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_unauthenticated_rejected(self, client):
        r = client.get("/shipments")
        assert r.status_code in (401, 403)

    def test_viewer_can_read(self, client, viewer_header):
        r = client.get("/shipments", headers=viewer_header)
        assert r.status_code == 200

    def test_filter_pending(self, client, auth_header):
        r = client.get("/shipments?status=pending", headers=auth_header)
        assert r.status_code == 200
        for item in r.json():
            assert item["status"] == "pending"

    def test_filter_in_transit(self, client, auth_header):
        r = client.get("/shipments?status=in_transit", headers=auth_header)
        assert r.status_code == 200

    def test_filter_delivered(self, client, auth_header):
        r = client.get("/shipments?status=delivered", headers=auth_header)
        assert r.status_code == 200

    def test_filter_cancelled(self, client, auth_header):
        r = client.get("/shipments?status=cancelled", headers=auth_header)
        assert r.status_code == 200

    def test_invalid_status_422(self, client, auth_header):
        r = client.get("/shipments?status=not_a_real_status", headers=auth_header)
        assert r.status_code == 422

    def test_limit_param_respected(self, client, auth_header):
        r = client.get("/shipments?limit=3", headers=auth_header)
        assert r.status_code == 200
        assert len(r.json()) <= 3

    def test_limit_over_cap_rejected(self, client, auth_header):
        r = client.get("/shipments?limit=201", headers=auth_header)
        assert r.status_code == 422


class TestCreateShipment:
    @pytest.fixture(scope="class")
    def valid_ids(self, client, auth_header):
        prod_r = client.get("/products?page=1&page_size=1", headers=auth_header)
        inv_r  = client.get("/inventory?page=1&page_size=1", headers=auth_header)
        if prod_r.status_code != 200 or not prod_r.json().get("data"):
            pytest.skip("No products in DB")
        if inv_r.status_code != 200 or not inv_r.json().get("data"):
            pytest.skip("No inventory in DB")
        return (
            prod_r.json()["data"][0]["id"],
            inv_r.json()["data"][0]["store_id"],
        )

    def test_create_returns_201(self, client, auth_header, valid_ids):
        pid, sid = valid_ids
        r = client.post("/shipments",
                        json={"product_id": pid, "store_id": sid, "quantity": 1},
                        headers=auth_header)
        assert r.status_code == 201

    def test_create_response_shape(self, client, auth_header, valid_ids):
        pid, sid = valid_ids
        r = client.post("/shipments",
                        json={"product_id": pid, "store_id": sid, "quantity": 2},
                        headers=auth_header)
        assert r.status_code == 201
        body = r.json()
        assert body["product_id"] == pid
        assert body["store_id"]   == sid
        assert body["quantity"]   == 2
        assert "status" in body
        assert "id" in body

    def test_create_invalid_product_404(self, client, auth_header):
        r = client.post("/shipments",
                        json={"product_id": 999999, "store_id": 1, "quantity": 1},
                        headers=auth_header)
        assert r.status_code == 404

    def test_create_unauthenticated_rejected(self, client):
        r = client.post("/shipments",
                        json={"product_id": 1, "store_id": 1, "quantity": 1})
        assert r.status_code in (401, 403)

    def test_create_zero_quantity_rejected(self, client, auth_header, valid_ids):
        pid, sid = valid_ids
        r = client.post("/shipments",
                        json={"product_id": pid, "store_id": sid, "quantity": 0},
                        headers=auth_header)
        assert r.status_code == 422
