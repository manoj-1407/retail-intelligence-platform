import psycopg2
from psycopg2 import pool as pg_pool
from .config import settings
import threading

_pool: pg_pool.ThreadedConnectionPool | None = None
_lock = threading.Lock()


def _get_pool() -> pg_pool.ThreadedConnectionPool:
    global _pool
    if _pool is None:
        with _lock:
            if _pool is None:
                _pool = pg_pool.ThreadedConnectionPool(
                    minconn=2,
                    maxconn=20,
                    host=settings.db_host,
                    port=settings.db_port,
                    dbname=settings.db_name,
                    user=settings.db_user,
                    password=settings.db_pass,
                    connect_timeout=3,
                )
    return _pool


def get_connection():
    return _get_pool().getconn()


def release_connection(conn):
    _get_pool().putconn(conn)


def execute_query(sql: str, params=None, fetch: bool = True):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(sql, params or ())
        if fetch:
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description] if cur.description else []
            cur.close()
            return [dict(zip(cols, row)) for row in rows]
        conn.commit()
        affected = cur.rowcount
        cur.close()
        return affected
    except Exception:
        conn.rollback()
        raise
    finally:
        release_connection(conn)


def execute_write(query: str, params: dict | None = None) -> None:
    """Execute an INSERT/UPDATE/DELETE query."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params or {})
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
