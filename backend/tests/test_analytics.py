"""
Analytics endpoint tests.

The /analytics/summary endpoint returns a rich payload used directly
by the React dashboard. These tests assert every field the frontend
depends on is present and correctly typed — if the contract breaks,
tests break before the user sees a broken chart.
"""
from __future__ import annotations


def test_analytics_summary_status(client, auth_header):
    r = client.get("/analytics/summary", headers=auth_header)
    assert r.status_code == 200


def test_analytics_kpis_present(client, auth_header):
    data = client.get("/analytics/summary", headers=auth_header).json()
    for field in ["total_products", "total_stores", "total_inventory",
                  "total_shipments", "low_stock_count", "low_stock_alerts",
                  "pending_shipments", "delivered_shipments"]:
        assert field in data, f"Missing field: {field}"
        assert isinstance(data[field], int), f"{field} must be int, got {type(data[field])}"


def test_analytics_categories_shape(client, auth_header):
    data = client.get("/analytics/summary", headers=auth_header).json()
    assert "categories" in data
    assert isinstance(data["categories"], list)
    if data["categories"]:
        row = data["categories"][0]
        assert "category"        in row
        assert "total_inventory" in row
        assert "avg_price"       in row
        assert isinstance(row["total_inventory"], int)
        assert isinstance(row["avg_price"], float)


def test_analytics_shipment_stats_shape(client, auth_header):
    data = client.get("/analytics/summary", headers=auth_header).json()
    assert "shipment_stats" in data
    assert isinstance(data["shipment_stats"], list)
    if data["shipment_stats"]:
        row = data["shipment_stats"][0]
        assert "status" in row
        assert "count"  in row
        assert isinstance(row["count"], int)


def test_analytics_low_stock_items_shape(client, auth_header):
    data = client.get("/analytics/summary", headers=auth_header).json()
    assert "low_stock_items" in data
    assert isinstance(data["low_stock_items"], list)
    if data["low_stock_items"]:
        row = data["low_stock_items"][0]
        assert "product_name"  in row
        assert "store_name"    in row
        assert "quantity"      in row
        assert "reorder_point" in row


def test_analytics_requires_auth(client):
    r = client.get("/analytics/summary")
    assert r.status_code == 403


def test_analytics_viewer_can_read(client, viewer_header):
    r = client.get("/analytics/summary", headers=viewer_header)
    assert r.status_code == 200


def test_analytics_low_stock_count_equals_alerts(client, auth_header):
    """Both field names must exist and agree — frontend and tests use different keys."""
    data = client.get("/analytics/summary", headers=auth_header).json()
    assert data["low_stock_count"] == data["low_stock_alerts"]


def test_analytics_kpis_non_negative(client, auth_header):
    data = client.get("/analytics/summary", headers=auth_header).json()
    for field in ["total_products", "total_stores", "total_inventory",
                  "total_shipments", "low_stock_count"]:
        assert data[field] >= 0, f"{field} must be >= 0"
