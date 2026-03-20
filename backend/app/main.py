from __future__ import annotations
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from .api import auth, products, shipments, inventory, analytics, allocate
from .api import inventory_range, websocket
from .core.config import settings

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Retail Intelligence Platform",
    description="Redlock distributed locking, WebSocket live inventory push, paginated REST API, RBAC, FastAPI + PostgreSQL + Redis.",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def attach_request_id(request: Request, call_next):
    rid = request.headers.get("X-Request-Id", str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["X-Request-Id"] = rid
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-Id"],
    expose_headers=["X-Request-Id"],
)

app.include_router(auth.router)
app.include_router(products.router)
app.include_router(shipments.router)
app.include_router(inventory.router)
app.include_router(analytics.router)
app.include_router(allocate.router)
app.include_router(inventory_range.router)
app.include_router(websocket.router)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok", "service": "retail-intelligence-platform", "version": "1.0.0"}


@app.exception_handler(Exception)
async def _unhandled(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error", "message": "An unexpected error occurred"},
    )
