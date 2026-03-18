# Retail Intelligence Platform

A real-time retail data platform that ingests shipment and product data, processes it through a custom data pipeline, stores it in a normalized schema, and serves live analytics through a REST API and React dashboard.

## Architecture
```
CSV / Event Sources
       |
Custom MinHeap + ETL Pipeline (Python)
       |
PostgreSQL (normalized schema)     Redis (L1 cache)
       |                                |
FastAPI REST Service ────────────────────
       |
Kafka (stock-update events)
       |
Go stock-reporter microservice
       |
React Dashboard (Recharts)
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | Python 3.11, FastAPI |
| Frontend | React + Vite, Recharts |
| Database | PostgreSQL 15 |
| Cache | Redis 7 |
| Messaging | Apache Kafka |
| Stock Reporter | Go 1.21 |
| Containers | Docker Compose |

## Why Each Technology

- **PostgreSQL over MySQL**: MVCC concurrency, TIMESTAMPTZ, normalized schema with CHECK constraints, better analytics support
- **Redis**: Inventory counts read far more than written — sub-millisecond cache hits vs ~5ms DB queries
- **Kafka**: Durable event log for stock updates — replay capability, consumer group scaling
- **Go**: Goroutines cost ~2KB each vs ~1MB for OS threads — 10,000 concurrent store reporters cost 20MB
- **FastAPI**: Async-native, Pydantic validation, auto-generated Swagger docs, 2-3x faster than Flask

## Layers (Build Order)

1. Database schema — normalized tables, indexes, seed data
2. MinHeap + ETL pipeline — custom data structure, CSV ingestion, pytest
3. FastAPI backend — CRUD endpoints, JWT auth, Redis caching
4. Segment Tree — O(log n) range inventory queries
5. Redlock — distributed locking for race-free stock allocation
6. Go stock-reporter — goroutines, Kafka producer
7. Kafka consumer — async stock update processing
8. React dashboard — live charts, inventory analytics

## Running Locally
```bash
# Start infrastructure
docker-compose up -d postgres redis zookeeper kafka

# Initialize database
cd database && bash init.sh

# Run tests
cd backend && pytest

# Start API
cd backend && uvicorn app.main:app --reload

# Start dashboard
cd frontend && npm run dev
```
