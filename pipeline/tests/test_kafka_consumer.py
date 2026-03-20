import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../kafka_consumer"))
from consumer import process_event


def test_valid_event():
    assert process_event({"store_id": 1, "product_id": 1, "quantity": 50}) is True


def test_negative_quantity_skipped():
    assert process_event({"store_id": 1, "product_id": 1, "quantity": -1}) is False


def test_missing_key():
    assert process_event({"store_id": 1, "product_id": 1}) is False


def test_zero_quantity_allowed():
    assert process_event({"store_id": 1, "product_id": 1, "quantity": 0}) is True


def test_string_quantity_coerced():
    assert process_event({"store_id": 1, "product_id": 1, "quantity": "25"}) is True
