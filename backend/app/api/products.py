from fastapi import APIRouter, Depends, Query, Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..core.database import execute_query
from ..core.security import get_current_user, require_admin
from ..schemas.product import ProductCreate

router = APIRouter(prefix="/products", tags=["products"])
limiter = Limiter(key_func=get_remote_address)


@router.get("")
@limiter.limit("60/minute")
def list_products(
    request: Request,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    category: str | None = Query(default=None),
    search: str | None = Query(default=None),
    user: dict = Depends(get_current_user),
):
    conditions: list[str] = []
    params: list = []
    if category:
        conditions.append("category = %s")
        params.append(category)
    if search:
        conditions.append("(name ILIKE %s OR sku ILIKE %s OR category ILIKE %s)")
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    offset = (page - 1) * page_size
    total_rows = execute_query(f"SELECT COUNT(*) AS n FROM products {where}", params)
    total = total_rows[0]["n"] if total_rows else 0
    rows = execute_query(
        f"SELECT * FROM products {where} ORDER BY id LIMIT %s OFFSET %s",
        params + [page_size, offset],
    )
    return {
        "data": rows or [],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": max(1, (total + page_size - 1) // page_size),
        },
    }


@router.get("/{product_id}")
@limiter.limit("60/minute")
def get_product(
    request: Request,
    product_id: int,
    user: dict = Depends(get_current_user),
):
    rows = execute_query("SELECT * FROM products WHERE id = %s", [product_id])
    if not rows:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return rows[0]


@router.post("", status_code=201)
@limiter.limit("30/minute")
def create_product(
    request: Request,
    body: ProductCreate,
    user: dict = Depends(require_admin),
):
    if float(body.unit_price) <= float(body.unit_cost):
        raise HTTPException(status_code=422, detail="unit_price must exceed unit_cost")
    rows = execute_query(
        "INSERT INTO products (sku, name, category, unit_cost, unit_price) "
        "VALUES (%s, %s, %s, %s, %s) RETURNING *",
        [body.sku, body.name, body.category, float(body.unit_cost), float(body.unit_price)],
    )
    return rows[0]
