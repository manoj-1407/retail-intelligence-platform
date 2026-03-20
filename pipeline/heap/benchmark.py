import time
import heapq
import random
from heap import MinHeap


def benchmark(n: int):
    data = [random.randint(0, 1_000_000) for _ in range(n)]

    t0 = time.perf_counter()
    h = MinHeap()
    h.heapify(list(data))
    while h:
        h.extract_min()
    custom_ms = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    hq = list(data)
    heapq.heapify(hq)
    while hq:
        heapq.heappop(hq)
    heapq_ms = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    sl = list(data)
    result = []
    while sl:
        m = min(sl)
        sl.remove(m)
        result.append(m)
    sorted_ms = (time.perf_counter() - t0) * 1000

    print(f"n={n:>7,} | MinHeap={custom_ms:>8.2f}ms | "
          f"heapq={heapq_ms:>8.2f}ms | sorted_list={sorted_ms:>8.2f}ms | "
          f"speedup vs sorted={sorted_ms/custom_ms:.1f}x")


if __name__ == "__main__":
    print("MinHeap benchmark — heapify + full extract")
    print("-" * 75)
    for n in [100, 1_000, 5_000, 10_000]:
        benchmark(n)
