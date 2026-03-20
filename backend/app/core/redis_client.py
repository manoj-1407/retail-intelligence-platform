import json
import redis
from .config import settings

_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    global _client
    if _client is None:
        _client = redis.Redis(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2,
            retry_on_timeout=True,
        )
    return _client


def cache_get(key: str):
    try:
        raw = get_redis().get(key)
        return json.loads(raw) if raw else None
    except Exception:
        return None


def cache_set(key: str, value, ttl: int = 30):
    try:
        get_redis().setex(key, ttl, json.dumps(value, default=str))
    except Exception:
        pass


def cache_del(key: str):
    try:
        get_redis().delete(key)
    except Exception:
        pass


def cache_del_pattern(pattern: str):
    try:
        r = get_redis()
        keys = list(r.scan_iter(pattern))
        if keys:
            r.delete(*keys)
    except Exception:
        pass
