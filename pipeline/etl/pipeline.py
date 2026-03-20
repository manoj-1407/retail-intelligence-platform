"""
ETL Pipeline — Extract → Validate → Transform → Load

Design decisions:
  - Custom MinHeap used to process critical/high-priority shipments first
  - Priority order: critical=0, high=1, normal=2, low=3
  - Invalid rows are collected into a rejection log, not silently dropped
  - Batch insert (executemany) instead of row-by-row for performance
  - All DB operations in a single transaction — atomic load or full rollback

Why heap here?
  Imagine 10,000 shipments arriving at once. A "critical" stockout at a
  hurricane-zone store needs to be loaded and visible to the API before
  a routine "low" restocking. The heap enforces processing order by priority.
"""

import csv
import os
import sys
import json
import psycopg2
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List, Tuple

# Add parent to path so we can import heap
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from heap.heap import MinHeap

PRIORITY_MAP = {"critical": 0, "high": 1, "normal": 2, "low": 3}

DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", 5432)),
    "dbname":   os.getenv("DB_NAME", "retail_db"),
    "user":     os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASS", "REDACTED_SEE_ENV_EXAMPLE"),
}


@dataclass(order=False)
class ShipmentRecord:
    priority_val:  int        # 0=critical, used by heap
    shipment_ref:  str
    sku:           str
    store_code:    str
    quantity:      int
    priority:      str
    status:        str
    shipped_at:    datetime
    delivered_at:  Optional[datetime] = None

    def __lt__(self, other):
        return self.priority_val < other.priority_val


# ── Extract ───────────────────────────────────────────────────────────────────

def extract(csv_path: str) -> Tuple[List[dict], int]:
    rows = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows, len(rows)


# ── Validate + Transform ──────────────────────────────────────────────────────

def validate_and_transform(
    rows: List[dict],
    valid_skus: set,
    valid_store_codes: set,
) -> Tuple[List[ShipmentRecord], List[dict]]:

    records = []
    rejected = []

    for row in rows:
        errors = []

        sku        = row.get("sku", "").strip()
        store_code = row.get("store_code", "").strip()
        priority   = row.get("priority", "normal").strip().lower()
        status     = row.get("status", "pending").strip().lower()

        # Validate SKU
        if sku not in valid_skus:
            errors.append(f"unknown sku: {sku}")

        # Validate store code
        if store_code not in valid_store_codes:
            errors.append(f"unknown store_code: {store_code}")

        # Validate quantity
        try:
            qty = int(row.get("quantity", 0))
            if qty <= 0:
                errors.append(f"non-positive quantity: {qty}")
        except ValueError:
            errors.append(f"non-numeric quantity: {row.get('quantity')}")
            qty = 0

        # Validate priority
        if priority not in PRIORITY_MAP:
            priority = "normal"

        # Validate status
        valid_statuses = {"pending","in_transit","delivered","cancelled"}
        if status not in valid_statuses:
            status = "pending"

        # Parse dates
        try:
            shipped_at = datetime.fromisoformat(row.get("shipped_at", ""))
        except (ValueError, TypeError):
            errors.append("invalid shipped_at")
            shipped_at = None

        delivered_raw = row.get("delivered_at", "").strip()
        delivered_at = None
        if delivered_raw:
            try:
                delivered_at = datetime.fromisoformat(delivered_raw)
            except ValueError:
                pass  # null delivered_at is acceptable

        if errors:
            rejected.append({"row": row, "errors": errors})
            continue

        records.append(ShipmentRecord(
            priority_val = PRIORITY_MAP[priority],
            shipment_ref = row.get("shipment_ref", "").strip(),
            sku          = sku,
            store_code   = store_code,
            quantity     = qty,
            priority     = priority,
            status       = status,
            shipped_at   = shipped_at,
            delivered_at = delivered_at,
        ))

    return records, rejected


# ── Priority queue ordering ───────────────────────────────────────────────────

def order_by_priority(records: List[ShipmentRecord]) -> List[ShipmentRecord]:
    """
    Use custom MinHeap to pop records in priority order.
    critical (0) comes out first, low (3) comes out last.
    """
    heap = MinHeap(key=lambda r: r.priority_val)
    heap.heapify(records)
    ordered = []
    while heap:
        ordered.append(heap.extract_min())
    return ordered


# ── Load ──────────────────────────────────────────────────────────────────────

def load(records: List[ShipmentRecord], conn) -> int:
    """Batch insert into shipments. Returns rows inserted."""
    cur = conn.cursor()

    # Resolve product_id and store_id from SKU/store_code
    cur.execute("SELECT id, sku FROM products")
    sku_map = {row[1]: row[0] for row in cur.fetchall()}

    cur.execute("SELECT id, store_code FROM stores")
    store_map = {row[1]: row[0] for row in cur.fetchall()}

    batch = []
    for r in records:
        product_id = sku_map.get(r.sku)
        store_id   = store_map.get(r.store_code)
        if not product_id or not store_id:
            continue
        batch.append((
            product_id, store_id, r.quantity,
            r.status, r.shipped_at, r.delivered_at,
        ))

    if batch:
        cur.executemany(
            """
            INSERT INTO shipments (product_id, store_id, quantity, status, shipped_at, delivered_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            batch,
        )

    conn.commit()
    cur.close()
    return len(batch)


# ── Run pipeline ──────────────────────────────────────────────────────────────

def run(csv_path: str, dry_run: bool = False) -> dict:
    print(f"\n[ETL] Starting pipeline — source: {csv_path}")

    # Extract
    raw_rows, total = extract(csv_path)
    print(f"[ETL] Extracted {total} rows")

    # Fetch valid reference data
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT sku FROM products")
    valid_skus = {r[0] for r in cur.fetchall()}
    cur.execute("SELECT store_code FROM stores")
    valid_stores = {r[0] for r in cur.fetchall()}
    cur.close()

    # Validate + Transform
    records, rejected = validate_and_transform(raw_rows, valid_skus, valid_stores)
    print(f"[ETL] Valid: {len(records)}  Rejected: {len(rejected)}")

    # Order by priority (heap)
    ordered = order_by_priority(records)
    priority_counts = {}
    for r in ordered:
        priority_counts[r.priority] = priority_counts.get(r.priority, 0) + 1
    print(f"[ETL] Priority breakdown: {priority_counts}")

    # Write rejection log
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_path = os.path.join(base, "data", "rejected.json")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    with open(log_path, "w") as f:
        json.dump(rejected, f, indent=2, default=str)
    print(f"[ETL] Rejection log → {log_path}")

    inserted = 0
    if not dry_run:
        inserted = load(ordered, conn)
        print(f"[ETL] Loaded {inserted} shipments into PostgreSQL")
    else:
        print("[ETL] Dry run — no DB writes")

    conn.close()

    return {
        "total_rows":    total,
        "valid_rows":    len(records),
        "rejected_rows": len(rejected),
        "inserted":      inserted,
        "priority_breakdown": priority_counts,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Retail ETL Pipeline")
    parser.add_argument("--csv",     default=None,   help="Path to input CSV")
    parser.add_argument("--dry-run", action="store_true", help="Skip DB write")
    args = parser.parse_args()

    if not args.csv:
        # Auto-generate CSV if none provided
        from generate_csv import generate
        csv_path = generate(500)
    else:
        csv_path = args.csv

    result = run(csv_path, dry_run=args.dry_run)
    print(f"\n[ETL] Summary: {result}")
