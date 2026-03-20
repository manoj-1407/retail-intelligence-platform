from typing import Callable, TypeVar

T = TypeVar("T", int, float)


class SegmentTree:
    """
    Generic segment tree supporting point updates and range queries.
    Supports sum, min, and max operations.
    Build: O(n). Query: O(log n). Update: O(log n).
    """

    def __init__(self, data: list[T], operation: Callable, identity: T):
        self._n   = len(data)
        self._op  = operation
        self._id  = identity
        self._tree: list[T] = [identity] * (2 * self._n)
        self._build(data)

    def _build(self, data: list[T]):
        for i, val in enumerate(data):
            self._tree[self._n + i] = val
        for i in range(self._n - 1, 0, -1):
            self._tree[i] = self._op(self._tree[2 * i], self._tree[2 * i + 1])

    def update(self, idx: int, value: T):
        pos = idx + self._n
        self._tree[pos] = value
        pos >>= 1
        while pos >= 1:
            self._tree[pos] = self._op(self._tree[2 * pos], self._tree[2 * pos + 1])
            pos >>= 1

    def query(self, left: int, right: int) -> T:
        """Range query [left, right] inclusive."""
        result = self._id
        left  += self._n
        right += self._n + 1
        while left < right:
            if left & 1:
                result = self._op(result, self._tree[left])
                left += 1
            if right & 1:
                right -= 1
                result = self._op(result, self._tree[right])
            left  >>= 1
            right >>= 1
        return result


class InventorySegmentTree:
    """
    Three simultaneous segment trees over the same store inventory data:
    one for sum queries, one for min, one for max.
    This answers 'total/min/max stock across stores L to R' in O(log n).
    """

    def __init__(self, quantities: list[int]):
        self._n = len(quantities)
        self._sum_tree = SegmentTree(quantities, lambda a, b: a + b, 0)
        self._min_tree = SegmentTree(quantities, min, float("inf"))
        self._max_tree = SegmentTree(quantities, max, float("-inf"))

    def update(self, store_index: int, new_quantity: int):
        self._sum_tree.update(store_index, new_quantity)
        self._min_tree.update(store_index, new_quantity)
        self._max_tree.update(store_index, new_quantity)

    def range_sum(self, left: int, right: int) -> int:
        return self._sum_tree.query(left, right)

    def range_min(self, left: int, right: int) -> int:
        v = self._min_tree.query(left, right)
        return int(v) if v != float("inf") else 0

    def range_max(self, left: int, right: int) -> int:
        v = self._max_tree.query(left, right)
        return int(v) if v != float("-inf") else 0

    def __len__(self):
        return self._n
