from fastapi import APIRouter, HTTPException, Depends, Query, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..schemas.shipment import ShipmentCreate, ShipmentOut
from ..core.database import execute_query
from ..core.redis_client import cache_get, cache_set
from ..core.security import get_current_user

router = APIRouter(prefix="/shipments", tags=["shipments"])
limiter = Limiter(key_func=get_remote_address)

VALID_STATUSES = {"pending", "in_transit", "delivered", "cancelled"}


@router.get("", response_model=list[ShipmentOut])
@limiter.limit("60/minute")
def list_shipments(
    request: Request,
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    user: dict = Depends(get_current_user),
):
    if status and status not in VALID_STATUSES:
        raise HTTPException(status_code=422,
            detail=f"status must be one of {sorted(VALID_STATUSES)}")
    cache_key = f"shipments:{status or 'all'}:{limit}"
    cached = cache_get(cache_key)
    if cached:
        return cached
    if status:
        rows = execute_query(
            "SELECT * FROM shipments WHERE status = %s ORDER BY created_at DESC LIMIT %s",
            (status, limit),
        )
    else:
        rows = execute_query(
            "SELECT * FROM shipments ORDER BY created_at DESC LIMIT %s", (limit,)
        )
    cache_set(cache_key, rows, ttl=15)
    return rows


@router.post("", response_model=ShipmentOut, status_code=201)
def create_shipment(body: ShipmentCreate, user: dict = Depends(get_current_user)):
    products = execute_query("SELECT id FROM products WHERE id = %s", (body.product_id,))
    if not products:
        raise HTTPException(status_code=404, detail="Product not found")
    stores = execute_query("SELECT id FROM stores WHERE id = %s", (body.store_id,))
    if not stores:
        raise HTTPException(status_code=404, detail="Store not found")
    rows = execute_query(
        """INSERT INTO shipments (product_id, store_id, quantity)
           VALUES (%s, %s, %s) RETURNING *""",
        (body.product_id, body.store_id, body.quantity),
    )
    return rows[0]
