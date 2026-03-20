"""pytest tests for MinHeap and MaxHeap — uses actual API."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import random
from heap.heap import MinHeap, MaxHeap


class TestMinHeap:

    def test_insert_extract_sorted_order(self):
        h = MinHeap()
        for x in [5, 1, 3, 9, 2]:
            h.insert(x)
        result = []
        while h:
            result.append(h.extract_min())
        assert result == sorted([5, 1, 3, 9, 2])

    def test_peek_min_does_not_remove(self):
        h = MinHeap()
        h.insert(10)
        h.insert(3)
        assert h.peek_min() == 3
        assert len(h) == 2

    def test_empty_extract_raises(self):
        h = MinHeap()
        with pytest.raises((IndexError, Exception)):
            h.extract_min()

    def test_single_element(self):
        h = MinHeap()
        h.insert(42)
        assert h.peek_min() == 42
        assert h.extract_min() == 42
        assert not h

    def test_large_random(self):
        data = [random.randint(-10000, 10000) for _ in range(500)]
        h = MinHeap()
        for x in data:
            h.insert(x)
        result = []
        while h:
            result.append(h.extract_min())
        assert result == sorted(data)

    def test_duplicates(self):
        h = MinHeap()
        for x in [3, 3, 1, 1, 2]:
            h.insert(x)
        assert h.extract_min() == 1
        assert h.extract_min() == 1
        assert h.extract_min() == 2

    def test_heapify(self):
        data = list(range(100, 0, -1))
        h = MinHeap()
        h.heapify(data)
        result = []
        while h:
            result.append(h.extract_min())
        assert result == sorted(data)

    def test_len_tracking(self):
        h = MinHeap()
        assert len(h) == 0
        h.insert(1)
        h.insert(2)
        assert len(h) == 2
        h.extract_min()
        assert len(h) == 1

    def test_custom_key(self):
        h = MinHeap(key=lambda x: x[1])
        h.insert(("a", 5))
        h.insert(("b", 1))
        h.insert(("c", 3))
        assert h.extract_min() == ("b", 1)
        assert h.extract_min() == ("c", 3)
        assert h.extract_min() == ("a", 5)


class TestMaxHeap:

    def test_insert_extract_reverse_order(self):
        h = MaxHeap()
        for x in [5, 1, 3, 9, 2]:
            h.insert(x)
        result = []
        while h:
            result.append(h.extract_max())
        assert result == sorted([5, 1, 3, 9, 2], reverse=True)

    def test_peek_max_is_maximum(self):
        h = MaxHeap()
        h.insert(7)
        h.insert(100)
        h.insert(3)
        assert h.peek_max() == 100

    def test_len_tracking(self):
        h = MaxHeap()
        assert len(h) == 0
        h.insert(1)
        h.insert(2)
        assert len(h) == 2
        h.extract_max()
        assert len(h) == 1

    def test_single_element(self):
        h = MaxHeap()
        h.insert(99)
        assert h.extract_max() == 99
        assert not h

    def test_custom_key_max(self):
        h = MaxHeap(key=lambda x: x["score"])
        h.insert({"name": "Alice", "score": 85})
        h.insert({"name": "Bob",   "score": 92})
        h.insert({"name": "Carol", "score": 78})
        assert h.extract_max()["name"] == "Bob"
        assert h.extract_max()["name"] == "Alice"
        assert h.extract_max()["name"] == "Carol"


class TestShipmentPriority:
    """Priority ordering using MinHeap — mirrors real ETL usage."""

    def test_critical_first(self):
        from etl.pipeline import ShipmentRecord, order_by_priority, PRIORITY_MAP
        from datetime import datetime, timezone

        def make(priority, ref):
            return ShipmentRecord(
                priority_val=PRIORITY_MAP[priority],
                shipment_ref=ref, sku="ELEC-001",
                store_code="WMT-TX-001", quantity=10,
                priority=priority, status="pending",
                shipped_at=datetime.now(timezone.utc).replace(tzinfo=None),
            )

        records = [
            make("low",      "SHP-LOW"),
            make("critical", "SHP-CRIT"),
            make("normal",   "SHP-NORM"),
            make("high",     "SHP-HIGH"),
        ]
        ordered = order_by_priority(records)
        assert ordered[0].priority == "critical"
        assert ordered[1].priority == "high"
        assert ordered[2].priority == "normal"
        assert ordered[3].priority == "low"
