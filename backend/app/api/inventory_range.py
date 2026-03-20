import time
from fastapi import APIRouter, Depends, Query
from ..schemas.analytics import RangeQueryResult
from ..core.database import execute_query
from ..core.security import get_current_user

router = APIRouter(prefix="/inventory/range", tags=["inventory"])


@router.get("", response_model=RangeQueryResult)
def range_query(
    product_id: int = Query(gt=0),
    store_id_start: int = Query(gt=0),
    store_id_end: int = Query(gt=0),
    user: dict = Depends(get_current_user),
):
    start = time.perf_counter()
    rows = execute_query(
        """SELECT quantity FROM inventory
           WHERE product_id = %s AND store_id BETWEEN %s AND %s""",
        (product_id, store_id_start, store_id_end),
    )
    total = sum(r["quantity"] for r in rows)
    elapsed = (time.perf_counter() - start) * 1000
    return RangeQueryResult(
        product_id=product_id,
        store_id_start=store_id_start,
        store_id_end=store_id_end,
        total_quantity=total,
        query_time_ms=round(elapsed, 3),
    )
