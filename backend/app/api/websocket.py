from __future__ import annotations
import asyncio
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from ..core.security import decode_token
from ..core.database import execute_query

router = APIRouter(tags=["websocket"])
_connections: list[WebSocket] = []
_connections_lock = asyncio.Lock()

_LOW_STOCK_SQL = (
    "SELECT p.name, s.name AS store, i.quantity, i.reorder_point "
    "FROM inventory i "
    "JOIN products p ON p.id = i.product_id "
    "JOIN stores   s ON s.id = i.store_id "
    "WHERE i.quantity <= i.reorder_point "
    "ORDER BY i.quantity ASC LIMIT 20"
)


@router.websocket("/ws/inventory")
async def inventory_feed(
    websocket: WebSocket,
    token: str = Query(..., description="JWT — required"),
):
    try:
        decode_token(token)
    except Exception:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    await websocket.accept()
    async with _connections_lock:
        _connections.append(websocket)

    try:
        while True:
            # Run the synchronous psycopg2 call in a thread pool so the
            # event loop is never blocked while the DB query is in flight.
            rows = await asyncio.to_thread(execute_query, _LOW_STOCK_SQL)
            payload = [
                {
                    "product":       r["name"],
                    "store":         r["store"],
                    "quantity":      r["quantity"],
                    "reorder_point": r["reorder_point"],
                }
                for r in (rows or [])
            ]
            await websocket.send_text(json.dumps({"type": "low_stock", "data": payload}))
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass
    finally:
        async with _connections_lock:
            if websocket in _connections:
                _connections.remove(websocket)
