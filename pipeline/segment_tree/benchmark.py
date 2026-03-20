import time
import random
from segment_tree import InventorySegmentTree


def benchmark_range_query(n: int, query_count: int = 1000):
    data = [random.randint(0, 500) for _ in range(n)]
    tree = InventorySegmentTree(data)
    queries = [(random.randint(0, n // 2), random.randint(n // 2, n - 1))
               for _ in range(query_count)]

    t0 = time.perf_counter()
    for l, r in queries:
        tree.range_sum(l, r)
    seg_ms = (time.perf_counter() - t0) * 1000

    t0 = time.perf_counter()
    for l, r in queries:
        sum(data[l:r + 1])
    naive_ms = (time.perf_counter() - t0) * 1000

    print(f"n={n:>7,} | {query_count} queries | "
          f"SegTree={seg_ms:>8.2f}ms | "
          f"Naive={naive_ms:>8.2f}ms | "
          f"speedup={naive_ms/seg_ms:.1f}x")


if __name__ == "__main__":
    print("Segment Tree range-sum benchmark (1000 queries per n)")
    print("-" * 70)
    for n in [100, 1_000, 5_000, 10_000]:
        benchmark_range_query(n)
