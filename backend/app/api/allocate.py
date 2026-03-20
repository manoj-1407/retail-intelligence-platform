import time
from fastapi import APIRouter, HTTPException, Depends
from ..schemas.inventory import AllocateRequest, AllocateResponse
from ..core.database import execute_query
from ..core.redis_client import cache_get, cache_set, cache_del
from ..core.redlock import inventory_lock, LockAcquisitionError
from ..core.security import get_current_user

router = APIRouter(prefix="/allocate", tags=["inventory"])


@router.post("", response_model=AllocateResponse)
def allocate_stock(body: AllocateRequest, user: dict = Depends(get_current_user)):
    start = time.perf_counter()
    try:
        with inventory_lock(body.product_id, body.store_id, ttl_ms=8000):
            cache_key = f"inv:{body.product_id}:{body.store_id}"
            cached = cache_get(cache_key)
            if cached is not None:
                current_qty = int(cached)
            else:
                rows = execute_query(
                    "SELECT quantity FROM inventory WHERE product_id = %s AND store_id = %s",
                    (body.product_id, body.store_id),
                )
                if not rows:
                    raise HTTPException(status_code=404,
                        detail="No inventory record for this product/store combination")
                current_qty = rows[0]["quantity"]

            if current_qty < body.quantity:
                raise HTTPException(status_code=409,
                    detail=f"Insufficient stock: requested {body.quantity}, available {current_qty}")

            new_qty = current_qty - body.quantity
            execute_query(
                """UPDATE inventory SET quantity = %s, updated_at = NOW()
                   WHERE product_id = %s AND store_id = %s""",
                (new_qty, body.product_id, body.store_id),
                fetch=False,
            )
            cache_set(cache_key, new_qty, ttl=30)
            cache_del("analytics:summary")

            elapsed = (time.perf_counter() - start) * 1000
            return AllocateResponse(
                success=True,
                allocated=body.quantity,
                remaining=new_qty,
                locked_ms=round(elapsed, 2),
            )
    except LockAcquisitionError:
        raise HTTPException(status_code=409,
            detail="Stock is being allocated by another request — retry in a moment")
