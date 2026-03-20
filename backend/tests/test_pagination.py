from __future__ import annotations


def test_products_pagination_shape(client, auth_header):
    r = client.get("/products?page=1&page_size=5", headers=auth_header)
    assert r.status_code == 200
    body = r.json()
    assert "data" in body
    assert "pagination" in body
    p = body["pagination"]
    assert p["page"] == 1
    assert p["page_size"] == 5
    assert "total" in p
    assert "total_pages" in p


def test_products_page_zero_invalid(client, auth_header):
    r = client.get("/products?page=0", headers=auth_header)
    assert r.status_code == 422


def test_products_page_size_over_cap(client, auth_header):
    r = client.get("/products?page_size=999", headers=auth_header)
    assert r.status_code == 422


def test_inventory_pagination_shape(client, auth_header):
    r = client.get("/inventory?page=1&page_size=10", headers=auth_header)
    assert r.status_code == 200
    body = r.json()
    assert "data" in body
    assert "pagination" in body


def test_products_search_returns_200(client, auth_header):
    r = client.get("/products?search=a", headers=auth_header)
    assert r.status_code == 200
    assert "data" in r.json()


def test_product_not_found(client, auth_header):
    r = client.get("/products/999999", headers=auth_header)
    assert r.status_code == 404


def test_request_id_generated(client):
    r = client.get("/health")
    assert "x-request-id" in r.headers


def test_request_id_echoed(client):
    r = client.get("/health", headers={"X-Request-Id": "trace-abc-123"})
    assert r.headers.get("x-request-id") == "trace-abc-123"
