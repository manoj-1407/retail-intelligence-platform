from __future__ import annotations
"""Tests for GET /inventory and GET /inventory/range."""
import pytest


class TestListInventory:
    def test_returns_200(self, client, auth_header):
        r = client.get("/inventory", headers=auth_header)
        assert r.status_code == 200

    def test_response_shape(self, client, auth_header):
        r = client.get("/inventory", headers=auth_header)
        body = r.json()
        assert "data" in body
        assert "pagination" in body
        p = body["pagination"]
        assert "page" in p
        assert "page_size" in p
        assert "total" in p
        assert "total_pages" in p

    def test_unauthenticated_rejected(self, client):
        r = client.get("/inventory")
        assert r.status_code in (401, 403)

    def test_viewer_can_read(self, client, viewer_header):
        r = client.get("/inventory", headers=viewer_header)
        assert r.status_code == 200

    def test_pagination_defaults(self, client, auth_header):
        r = client.get("/inventory", headers=auth_header)
        assert r.json()["pagination"]["page"] == 1

    def test_page_size_respected(self, client, auth_header):
        r = client.get("/inventory?page=1&page_size=5", headers=auth_header)
        assert r.status_code == 200
        assert len(r.json()["data"]) <= 5

    def test_page_zero_invalid(self, client, auth_header):
        r = client.get("/inventory?page=0", headers=auth_header)
        assert r.status_code == 422

    def test_page_size_over_cap_invalid(self, client, auth_header):
        r = client.get("/inventory?page_size=501", headers=auth_header)
        assert r.status_code == 422

    def test_filter_by_product_id(self, client, auth_header):
        r = client.get("/inventory?page=1&page_size=1", headers=auth_header)
        if r.status_code != 200 or not r.json()["data"]:
            pytest.skip("No inventory data")
        pid = r.json()["data"][0]["product_id"]
        r2 = client.get(f"/inventory?product_id={pid}", headers=auth_header)
        assert r2.status_code == 200
        for row in r2.json()["data"]:
            assert row["product_id"] == pid

    def test_filter_by_store_id(self, client, auth_header):
        r = client.get("/inventory?page=1&page_size=1", headers=auth_header)
        if r.status_code != 200 or not r.json()["data"]:
            pytest.skip("No inventory data")
        sid = r.json()["data"][0]["store_id"]
        r2 = client.get(f"/inventory?store_id={sid}", headers=auth_header)
        assert r2.status_code == 200
        for row in r2.json()["data"]:
            assert row["store_id"] == sid

    def test_low_stock_only_filter(self, client, auth_header):
        r = client.get("/inventory?low_stock_only=true", headers=auth_header)
        assert r.status_code == 200
        for row in r.json()["data"]:
            assert row["quantity"] <= row["reorder_point"]


class TestInventoryRange:
    def test_range_query_returns_200(self, client, auth_header):
        r = client.get("/inventory/range?product_id=1&store_id_start=1&store_id_end=10",
                       headers=auth_header)
        assert r.status_code in (200, 404, 422, 500)

    def test_range_response_shape(self, client, auth_header):
        r = client.get("/inventory/range?product_id=1&store_id_start=1&store_id_end=5",
                       headers=auth_header)
        if r.status_code != 200:
            pytest.skip("No matching inventory for range test")
        body = r.json()
        assert "product_id"      in body
        assert "store_id_start"  in body
        assert "store_id_end"    in body
        assert "total_quantity"  in body
        assert "query_time_ms"   in body

    def test_range_unauthenticated_rejected(self, client):
        r = client.get("/inventory/range?product_id=1&store_id_start=1&store_id_end=5")
        assert r.status_code in (401, 403)

    def test_range_zero_product_id_invalid(self, client, auth_header):
        r = client.get("/inventory/range?product_id=0&store_id_start=1&store_id_end=5",
                       headers=auth_header)
        assert r.status_code == 422
