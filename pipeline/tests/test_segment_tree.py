import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../segment_tree"))
from segment_tree import InventorySegmentTree, SegmentTree


def test_range_sum_full():
    data = [10, 20, 30, 40, 50]
    tree = InventorySegmentTree(data)
    assert tree.range_sum(0, 4) == 150


def test_range_sum_partial():
    data = [5, 10, 15, 20, 25]
    tree = InventorySegmentTree(data)
    assert tree.range_sum(1, 3) == 45


def test_range_sum_single_element():
    data = [42]
    tree = InventorySegmentTree(data)
    assert tree.range_sum(0, 0) == 42


def test_range_min():
    data = [8, 3, 7, 1, 9]
    tree = InventorySegmentTree(data)
    assert tree.range_min(0, 4) == 1
    assert tree.range_min(0, 2) == 3


def test_range_max():
    data = [8, 3, 7, 1, 9]
    tree = InventorySegmentTree(data)
    assert tree.range_max(0, 4) == 9
    assert tree.range_max(0, 1) == 8


def test_point_update_propagates():
    data = [10, 20, 30, 40, 50]
    tree = InventorySegmentTree(data)
    tree.update(2, 100)
    assert tree.range_sum(0, 4) == 220
    assert tree.range_max(0, 4) == 100


def test_update_to_zero():
    data = [10, 20, 30]
    tree = InventorySegmentTree(data)
    tree.update(1, 0)
    assert tree.range_sum(0, 2) == 40
    assert tree.range_min(0, 2) == 0


def test_large_n():
    n = 1000
    data = list(range(1, n + 1))
    tree = InventorySegmentTree(data)
    expected = sum(range(1, n + 1))
    assert tree.range_sum(0, n - 1) == expected


def test_consistency_with_naive():
    import random
    n = 200
    data = [random.randint(0, 100) for _ in range(n)]
    tree = InventorySegmentTree(data)
    for _ in range(50):
        l = random.randint(0, n // 2)
        r = random.randint(n // 2, n - 1)
        assert tree.range_sum(l, r) == sum(data[l:r + 1])
