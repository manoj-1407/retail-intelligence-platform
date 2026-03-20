"""
pytest tests for ETL validation and transformation logic.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from etl.pipeline import validate_and_transform

VALID_SKUS   = {"ELEC-001", "ELEC-002", "GROC-001"}
VALID_STORES = {"WMT-TX-001", "WMT-CA-001"}

def make_row(**kwargs):
    defaults = {
        "shipment_ref": "SHP-00001",
        "sku":          "ELEC-001",
        "store_code":   "WMT-TX-001",
        "quantity":     "50",
        "priority":     "normal",
        "status":       "pending",
        "shipped_at":   "2024-01-15T10:00:00",
        "delivered_at": "",
    }
    defaults.update(kwargs)
    return defaults


class TestValidateTransform:

    def test_valid_row_accepted(self):
        rows = [make_row()]
        records, rejected = validate_and_transform(rows, VALID_SKUS, VALID_STORES)
        assert len(records) == 1
        assert len(rejected) == 0

    def test_invalid_sku_rejected(self):
        rows = [make_row(sku="INVALID-SKU")]
        records, rejected = validate_and_transform(rows, VALID_SKUS, VALID_STORES)
        assert len(records) == 0
        assert len(rejected) == 1
        assert any("unknown sku" in e for e in rejected[0]["errors"])

    def test_negative_quantity_rejected(self):
        rows = [make_row(quantity="-10")]
        records, rejected = validate_and_transform(rows, VALID_SKUS, VALID_STORES)
        assert len(records) == 0
        assert len(rejected) == 1

    def test_zero_quantity_rejected(self):
        rows = [make_row(quantity="0")]
        records, rejected = validate_and_transform(rows, VALID_SKUS, VALID_STORES)
        assert len(records) == 0

    def test_invalid_store_rejected(self):
        rows = [make_row(store_code="FAKE-STORE")]
        records, rejected = validate_and_transform(rows, VALID_SKUS, VALID_STORES)
        assert len(rejected) == 1

    def test_unknown_priority_defaults_to_normal(self):
        rows = [make_row(priority="EXTREME")]
        records, rejected = validate_and_transform(rows, VALID_SKUS, VALID_STORES)
        assert len(records) == 1
        assert records[0].priority == "normal"

    def test_delivered_at_parsed(self):
        rows = [make_row(
            status="delivered",
            delivered_at="2024-01-20T15:30:00"
        )]
        records, _ = validate_and_transform(rows, VALID_SKUS, VALID_STORES)
        assert records[0].delivered_at is not None

    def test_mixed_batch(self):
        rows = [
            make_row(sku="ELEC-001"),         # valid
            make_row(sku="INVALID"),           # invalid sku
            make_row(quantity="-5"),           # invalid qty
            make_row(store_code="FAKE"),       # invalid store
            make_row(sku="GROC-001"),          # valid
        ]
        records, rejected = validate_and_transform(rows, VALID_SKUS, VALID_STORES)
        assert len(records) == 2
        assert len(rejected) == 3

    def test_priority_val_correct(self):
        rows = [
            make_row(priority="critical"),
            make_row(priority="high"),
        ]
        records, _ = validate_and_transform(rows, VALID_SKUS, VALID_STORES)
        assert records[0].priority_val == 0  # critical
        assert records[1].priority_val == 1  # high
