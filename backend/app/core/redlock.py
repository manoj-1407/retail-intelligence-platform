import time
import uuid
from contextlib import contextmanager
from .redis_client import get_redis

RELEASE_LUA = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
"""


class LockAcquisitionError(Exception):
    pass


def acquire_lock(key: str, ttl_ms: int = 5000, retries: int = 3,
                 retry_delay: float = 0.1) -> str | None:
    r = get_redis()
    token = str(uuid.uuid4())
    for attempt in range(retries):
        if r.set(key, token, px=ttl_ms, nx=True):
            return token
        if attempt < retries - 1:
            time.sleep(retry_delay)
    return None


def release_lock(key: str, token: str):
    try:
        get_redis().eval(RELEASE_LUA, 1, key, token)
    except Exception:
        pass


@contextmanager
def inventory_lock(product_id: int, store_id: int, ttl_ms: int = 5000):
    lock_key = f"lock:inv:{product_id}:{store_id}"
    token = acquire_lock(lock_key, ttl_ms=ttl_ms)
    if not token:
        raise LockAcquisitionError(
            f"Could not acquire lock for product={product_id} store={store_id}")
    try:
        yield token
    finally:
        release_lock(lock_key, token)
