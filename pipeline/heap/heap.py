from typing import TypeVar, Generic, Callable, Optional

T = TypeVar("T")


class MinHeap(Generic[T]):
    """
    Custom min-heap. Uses Floyd's O(n) bottom-up heapify.
    Supports a key function so you can heap arbitrary objects.

    Usage:
        heap = MinHeap(key=lambda x: x.priority)
        heap.insert(item)
        top = heap.extract_min()
    """

    def __init__(self, key: Callable[[T], any] = lambda x: x):
        self._data: list[T] = []
        self._key = key

    def _k(self, idx: int):
        return self._key(self._data[idx])

    def _swap(self, i: int, j: int):
        self._data[i], self._data[j] = self._data[j], self._data[i]

    def _sift_up(self, idx: int):
        while idx > 0:
            parent = (idx - 1) >> 1
            if self._k(idx) < self._k(parent):
                self._swap(idx, parent)
                idx = parent
            else:
                break

    def _sift_down(self, idx: int):
        n = len(self._data)
        while True:
            left  = 2 * idx + 1
            right = 2 * idx + 2
            smallest = idx
            if left < n and self._k(left) < self._k(smallest):
                smallest = left
            if right < n and self._k(right) < self._k(smallest):
                smallest = right
            if smallest == idx:
                break
            self._swap(idx, smallest)
            idx = smallest

    def insert(self, item: T):
        self._data.append(item)
        self._sift_up(len(self._data) - 1)

    def peek_min(self) -> T:
        if not self._data:
            raise IndexError("Heap is empty")
        return self._data[0]

    def extract_min(self) -> T:
        if not self._data:
            raise IndexError("Heap is empty")
        self._swap(0, len(self._data) - 1)
        item = self._data.pop()
        if self._data:
            self._sift_down(0)
        return item

    def heapify(self, items: list[T]):
        """Floyd's algorithm — O(n) build from list, better than n inserts."""
        self._data = list(items)
        for i in range(len(self._data) // 2 - 1, -1, -1):
            self._sift_down(i)

    def __len__(self):
        return len(self._data)

    def __bool__(self):
        return bool(self._data)


class MaxHeap(Generic[T]):
    """Max-heap backed by a MinHeap with negated key."""

    def __init__(self, key: Callable[[T], any] = lambda x: x):
        self._inner: MinHeap[T] = MinHeap(key=lambda x: -key(x))
        self._key = key

    def insert(self, item: T):
        self._inner.insert(item)

    def peek_max(self) -> T:
        return self._inner.peek_min()

    def extract_max(self) -> T:
        return self._inner.extract_min()

    def heapify(self, items: list[T]):
        self._inner.heapify(items)

    def __len__(self):
        return len(self._inner)
