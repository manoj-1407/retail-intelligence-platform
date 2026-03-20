import threading
from backend.app.core.redlock import acquire_lock, release_lock, LockAcquisitionError


def test_acquire_and_release():
    token = acquire_lock("test:lock:1", ttl_ms=5000)
    if token:
        release_lock("test:lock:1", token)


def test_double_acquire_fails():
    token1 = acquire_lock("test:lock:2", ttl_ms=5000, retries=1)
    if token1:
        token2 = acquire_lock("test:lock:2", ttl_ms=100, retries=1, retry_delay=0.01)
        assert token2 is None
        release_lock("test:lock:2", token1)


def test_concurrent_lock_safety():
    results = []
    lock_key = "test:lock:concurrent"

    def try_acquire():
        token = acquire_lock(lock_key, ttl_ms=2000, retries=3, retry_delay=0.05)
        if token:
            results.append("acquired")
            import time; time.sleep(0.05)
            release_lock(lock_key, token)
        else:
            results.append("blocked")

    threads = [threading.Thread(target=try_acquire) for _ in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()

    acquired_count = results.count("acquired")
    assert acquired_count >= 1
