from __future__ import annotations
from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from ..core.database import execute_query
from ..core.redis_client import cache_get, cache_set
from ..core.security import get_current_user

router  = APIRouter(prefix="/analytics", tags=["analytics"])
limiter = Limiter(key_func=get_remote_address)


@router.get("/summary")
@limiter.limit("30/minute")
def summary(request: Request, user: dict = Depends(get_current_user)) -> dict:
    """
    Returns a rich analytics payload consumed directly by the dashboard.

    Uses a single cache key with a 20-second TTL so burst reads hit Redis,
    not PostgreSQL. Cache is invalidated by allocate.py on stock changes.
    """
    cached = cache_get("analytics:summary")
    if cached:
        return cached

    # ── Scalar KPIs ─────────────────────────────────────────────────────────
    total_products  = execute_query("SELECT COUNT(*) AS n FROM products")[0]["n"]
    total_stores    = execute_query("SELECT COUNT(*) AS n FROM stores")[0]["n"]
    total_inv       = execute_query("SELECT COALESCE(SUM(quantity), 0) AS n FROM inventory")[0]["n"]
    total_shipments = execute_query("SELECT COUNT(*) AS n FROM shipments")[0]["n"]
    low_stock       = execute_query(
        "SELECT COUNT(*) AS n FROM inventory WHERE quantity <= reorder_point"
    )[0]["n"]
    pending_ship    = execute_query(
        "SELECT COUNT(*) AS n FROM shipments WHERE status = %s", ("pending",)
    )[0]["n"]
    delivered_ship  = execute_query(
        "SELECT COUNT(*) AS n FROM shipments WHERE status = %s", ("delivered",)
    )[0]["n"]

    # ── Category breakdown (for area chart) ─────────────────────────────────
    cat_rows = execute_query("""
        SELECT
            p.category,
            COALESCE(SUM(i.quantity), 0)            AS total_inventory,
            ROUND(AVG(p.unit_price)::numeric, 2)    AS avg_price
        FROM products p
        LEFT JOIN inventory i ON i.product_id = p.id
        GROUP BY p.category
        ORDER BY total_inventory DESC
    """)
    categories = [
        {
            "category":        r["category"],
            "total_inventory": int(r["total_inventory"]),
            "avg_price":       float(r["avg_price"] or 0),
        }
        for r in cat_rows
    ]

    # ── Shipment status breakdown (for donut chart) ──────────────────────────
    stat_rows = execute_query("""
        SELECT status, COUNT(*) AS count
        FROM shipments
        GROUP BY status
        ORDER BY count DESC
    """)
    shipment_stats = [{"status": r["status"], "count": int(r["count"])} for r in stat_rows]

    # ── Low-stock detail rows (for alert table) ──────────────────────────────
    low_rows = execute_query("""
        SELECT
            p.name  AS product_name,
            s.name  AS store_name,
            i.quantity,
            i.reorder_point
        FROM inventory i
        JOIN products p ON p.id = i.product_id
        JOIN stores   s ON s.id = i.store_id
        WHERE i.quantity <= i.reorder_point
        ORDER BY i.quantity ASC
        LIMIT 50
    """)
    low_stock_items = [
        {
            "product_name": r["product_name"],
            "store_name":   r["store_name"],
            "quantity":     int(r["quantity"]),
            "reorder_point": int(r["reorder_point"]),
        }
        for r in low_rows
    ]

    result = {
        # KPIs
        "total_products":     int(total_products),
        "total_stores":       int(total_stores),
        "total_inventory":    int(total_inv),
        "total_shipments":    int(total_shipments),
        "low_stock_count":    int(low_stock),    # aliased so frontend needs no change
        "low_stock_alerts":   int(low_stock),    # kept for backward-compat with tests
        "pending_shipments":  int(pending_ship),
        "delivered_shipments": int(delivered_ship),
        # Chart data
        "categories":         categories,
        "shipment_stats":     shipment_stats,
        "low_stock_items":    low_stock_items,
    }
    cache_set("analytics:summary", result, ttl=20)
    return result
