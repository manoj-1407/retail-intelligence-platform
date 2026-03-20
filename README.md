# Retail Intelligence Platform

[![CI](https://github.com/manoj-1407/retail-intelligence-platform/actions/workflows/ci.yml/badge.svg)](https://github.com/manoj-1407/retail-intelligence-platform/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![Go](https://img.shields.io/badge/Go-1.21-00ADD8?logo=go)
![Tests](https://img.shields.io/badge/tests-51%20passing-success)
![Redis](https://img.shields.io/badge/Redis-7-red?logo=redis)
![Kafka](https://img.shields.io/badge/Kafka-3.x-black?logo=apachekafka)

A full-stack retail intelligence system with a custom data structures pipeline, real-time WebSocket dashboard, distributed locking, and a Go Kafka producer — built to demonstrate systems-level thinking across the entire stack.

---

## Architecture
```
┌──────────────────────────────────────────────────────────────────────┐
│                   React 18 Dashboard (Vite + TS)                     │
│  Glassmorphism UI · Framer Motion · Recharts · Inventory Heatmap     │
│  Skeleton Loaders · Count-up KPIs · Animated Benchmarks Page         │
└──────────────────────────┬───────────────────────────────────────────┘
                           │ HTTP / WebSocket
┌──────────────────────────▼───────────────────────────────────────────┐
│                    FastAPI (Python 3.11)                             │
│                                                                      │
│  /auth/token    ──► JWT (admin/viewer roles)                         │
│  /products      ──► Pydantic V2 validation, Redis cache-aside        │
│  /inventory     ──► Range queries via Segment Tree O(log n)          │
│  /analytics/summary ──► Aggregated KPIs                              │
│  /allocate      ──► Redlock distributed locking (SET NX PX)          │
│  /ws/inventory  ──► WebSocket push every 5s                          │
│       │                                                              │
│  Redis 7 ───────────► Cache-aside (5 min TTL) + Redlock              │
│  Kafka Consumer ────► Processes stock-update events, invalidates cache│
└──────────────────────────┬───────────────────────────────────────────┘
                           │
         ┌─────────────────┼──────────────────┐
         │                 │                  │
   PostgreSQL 15      Redis 7           Apache Kafka
   (9 indexes,        (cache +          (stock-updates
    100 seed rows)     Redlock)          topic)
         ▲                                    ▲
         │                                    │
┌────────┴────────┐               ┌───────────┴──────────┐
│  ETL Pipeline   │               │  Go Stock Reporter   │
│  (Python)       │               │  (Go 1.21)           │
│  CSV → MinHeap  │               │  10 goroutines       │
│  → batch insert │               │  Sarama Kafka prod.  │
│  26x faster     │               │  one per store       │
└─────────────────┘               └──────────────────────┘
```

---

## The Data Structures Layer (What makes this unique)

Most portfolio projects use CRUD + a framework. This one implements the data structures from scratch and benchmarks them against naive alternatives in production.

### MinHeap / MaxHeap — ETL Pipeline
```python
# Custom heap implementation (not heapq) — O(log n) insert/extract
heap = MinHeap()
for row in csv_data:
    heap.insert((row.priority, row))       # O(log n)

# Extract in priority order for batch DB insert
while not heap.is_empty():
    _, item = heap.extract_min()           # O(log n)
    batch.append(item)
```

**Benchmark (n=10,000):**
```
MinHeap sort:    8ms   ← custom implementation
Sorted list:   211ms   ← Python's built-in sorted()
Speedup:        26x
```

### Segment Tree — Range Queries
```python
# O(log n) range sum/min/max — used for inventory range queries
tree = SegmentTree(store_quantities)
total = tree.range_sum(store_4, store_9)   # O(log n) vs O(n) naive
```

**Benchmark (n=10,000 stores):**
```
Segment Tree:  0.41ms   ← O(log n)
Naive array:  18.9ms    ← O(n)
Speedup:         9x
```

### Redlock — Distributed Locking
```python
# Race-safe stock allocation — no overselling under concurrent requests
# Uses SET NX PX + Lua atomic release script
async def allocate_stock(product_id, store_id, qty):
    async with redlock(f"stock:{product_id}:{store_id}"):
        # Only one request enters here at a time
        await db.execute(UPDATE inventory SET quantity = quantity - qty ...)
```

---

## Tech Stack

| Layer           | Technology                            | Why                                    |
|-----------------|---------------------------------------|----------------------------------------|
| Backend         | FastAPI + Python 3.11                 | Async, Pydantic V2, auto OpenAPI       |
| Data Structures | Custom MinHeap, MaxHeap, SegmentTree  | 26x and 9x speedups over naive         |
| Cache           | Redis 7 (cache-aside, 5 min TTL)      | Invalidated on writes + Redlock        |
| Messaging       | Apache Kafka + Go Sarama producer     | 10 goroutines, one per store           |
| Database        | PostgreSQL 15 (9 indexes, 100 rows)   | Normalized schema, optimised queries   |
| Auth            | JWT (admin/viewer roles)              | Pydantic V2 validated                  |
| Real-time       | WebSocket /ws/inventory               | Pushes every 5s with reconnect logic   |
| Frontend        | React 18 + Vite + TypeScript          | Glassmorphism, Framer Motion, Recharts |
| Tests           | pytest (51 passing) + Go tests (4)    | Heap, ETL, segment tree, Kafka, auth   |
| Migrations      | Alembic                               | Baseline migration, version-controlled |
| Logging         | structlog (JSON in prod, colour dev)  | Structured, context-bound              |
| CI              | GitHub Actions                        | Python + Go + frontend on every push   |

---

## Quick Start
```bash
# 1. Start infrastructure
docker-compose up -d    # postgres + redis + kafka + zookeeper

# 2. Seed database
cd backend && python3 -c "from app.db import seed; seed()"

# 3. Run backend
uvicorn app.main:app --reload --port 8000

# 4. Run frontend (new terminal)
cd frontend && npm install && npm run dev

# 5. (Optional) Run Go stock reporter
cd stock-reporter && go run .
```

API docs: http://localhost:8000/docs
Dashboard: http://localhost:5173

---

## Test Suite
```bash
# All 51 tests from project root (pytest.ini sets PYTHONPATH)
python3 -m pytest

# Breakdown:
# backend/tests/test_auth.py          JWT, roles, expiry
# backend/tests/test_products.py      CRUD, validation, margin calc
# backend/tests/test_analytics.py     Summary aggregations
# backend/tests/test_redlock.py       Lock acquire/release/contention
# pipeline/tests/test_heap.py         insert, extract_min/max, heapify
# pipeline/tests/test_etl.py          CSV → validate → heap sort → insert
# pipeline/tests/test_segment_tree.py range_sum, range_min, range_max
# pipeline/tests/test_kafka_consumer.py simulation mode, event processing
```

---

## Dashboard Features

| Page        | Features                                                              |
|-------------|-----------------------------------------------------------------------|
| Dashboard   | Count-up KPIs, gradient area charts, inventory heatmap, skeleton loaders |
| Products    | Card grid, debounced search, category filter pills, margin % badge    |
| Inventory   | Color-coded table (red/yellow/green), sparklines, table↔heatmap toggle |
| Shipments   | Status badges, animated entry                                         |
| Benchmarks  | Animated bar race (Heap vs List), segment tree self-builds, complexity table |
| Live Feed   | WebSocket ticker, reconnect logic, low-stock alerts                   |
| Live Alerts | Real-time alerts pushed via WebSocket                                 |

---

## Project Structure
```
retail-intelligence-platform/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app, routers, WebSocket
│   │   ├── auth.py          # JWT, roles
│   │   ├── models.py        # Pydantic V2 schemas
│   │   ├── db.py            # PostgreSQL, connection pool
│   │   ├── cache.py         # Redis cache-aside + Redlock
│   │   ├── segment_tree.py  # O(log n) range queries
│   │   └── logging_config.py # structlog JSON/colour setup
│   ├── alembic/             # Database migrations
│   └── tests/               # 13 backend tests
├── pipeline/
│   ├── heap.py              # MinHeap + MaxHeap from scratch
│   ├── etl.py               # CSV → validate → heap sort → batch insert
│   ├── segment_tree.py      # Segment tree range queries
│   ├── kafka_consumer.py    # Processes stock-update events
│   └── tests/               # 38 pipeline tests
├── stock-reporter/          # Go 1.21 Kafka producer
│   ├── main.go              # 10 goroutines, Sarama client
│   └── *_test.go            # 4 Go unit tests
├── frontend/                # React 18 + Vite + TS dashboard
├── docker-compose.yml       # Full stack: postgres+redis+kafka+zookeeper+backend
└── pytest.ini               # PYTHONPATH=. so tests run from root
```
