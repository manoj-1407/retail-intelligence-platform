from __future__ import annotations
from fastapi import APIRouter, Depends, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..core.database import execute_query
from ..core.redis_client import cache_get, cache_set
from ..core.security import get_current_user

router = APIRouter(prefix="/inventory", tags=["inventory"])
limiter = Limiter(key_func=get_remote_address)


@router.get("")
@limiter.limit("60/minute")
def list_inventory(
    request: Request,
    product_id: int | None = Query(default=None),
    store_id: int | None = Query(default=None),
    low_stock_only: bool = Query(default=False),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=500),
    user: dict = Depends(get_current_user),
):
    conditions: list[str] = []
    params: list = []

    if product_id is not None:
        conditions.append("product_id = %s")
        params.append(product_id)
    if store_id is not None:
        conditions.append("store_id = %s")
        params.append(store_id)
    if low_stock_only:
        conditions.append("quantity <= reorder_point")

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    offset = (page - 1) * page_size
    cache_key = f"inv:{product_id}:{store_id}:{low_stock_only}:{page}:{page_size}"

    cached = cache_get(cache_key)
    if cached:
        return cached

    total_rows = execute_query(f"SELECT COUNT(*) AS n FROM inventory {where}", params)
    total = total_rows[0]["n"] if total_rows else 0
    rows = execute_query(
        f"SELECT * FROM inventory {where} ORDER BY id LIMIT %s OFFSET %s",
        params + [page_size, offset],
    )

    result = {
        "data": rows or [],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": max(1, -(-total // page_size)),
        },
    }
    cache_set(cache_key, result, ttl=10)
    return result
