def test_list_products(client, auth_header):
    r = client.get("/products", headers=auth_header)
    assert r.status_code == 200
    assert isinstance(r.json()["data"], list)


def test_get_product_not_found(client, auth_header):
    r = client.get("/products/999999", headers=auth_header)
    assert r.status_code == 404


def test_viewer_cannot_create_product(client, viewer_header):
    r = client.post("/products", json={
        "sku": "VIEWER-SKU", "name": "Test", "category": "Test",
        "unit_cost": 10.0, "unit_price": 20.0,
    }, headers=viewer_header)
    assert r.status_code == 403


def test_price_must_exceed_cost(client, auth_header):
    r = client.post("/products", json={
        "sku": "BAD-PRICE", "name": "Bad", "category": "Test",
        "unit_cost": 50.0, "unit_price": 30.0,
    }, headers=auth_header)
    assert r.status_code == 422
