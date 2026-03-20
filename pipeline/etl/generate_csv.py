"""
Generate realistic CSV data for ETL pipeline testing.
Produces: pipeline/data/shipments_raw.csv
"""

import csv
import random
import os
from datetime import datetime, timedelta, timezone

SKUS = [
    "ELEC-001","ELEC-002","ELEC-003",
    "GROC-001","GROC-002",
    "CLTH-001","CLTH-002",
    "HOME-001","HOME-002",
    "TOYS-001",
]
STORE_CODES = [
    "WMT-TX-001","WMT-TX-002","WMT-CA-001","WMT-CA-002",
    "WMT-NY-001","WMT-FL-001","WMT-IL-001","WMT-WA-001",
    "WMT-GA-001","WMT-AZ-001",
]
STATUSES = ["pending","in_transit","delivered","cancelled"]
PRIORITIES = ["low","normal","high","critical"]

def generate(n: int = 500, output: str = None) -> str:
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base, "data")
    os.makedirs(data_dir, exist_ok=True)
    output = output or os.path.join(data_dir, "shipments_raw.csv")

    rows = []
    now = datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    for i in range(n):
        shipped = now - timedelta(days=random.randint(0, 30))
        delivered = None
        status = random.choices(STATUSES, weights=[20, 30, 45, 5])[0]
        if status == "delivered":
            delivered = shipped + timedelta(days=random.randint(1, 5))
        # Inject some dirty data for ETL to handle
        qty = random.randint(-5, 200)          # some negatives — invalid
        sku = random.choice(SKUS)
        if random.random() < 0.03:
            sku = "INVALID-SKU"                # ~3% bad SKUs
        rows.append({
            "shipment_ref":  f"SHP-{i+1:05d}",
            "sku":           sku,
            "store_code":    random.choice(STORE_CODES),
            "quantity":      qty,
            "priority":      random.choices(PRIORITIES, weights=[30, 50, 15, 5])[0],
            "status":        status,
            "shipped_at":    shipped.isoformat(),
            "delivered_at":  delivered.isoformat() if delivered else "",
        })

    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {n} rows → {output}")
    return output


if __name__ == "__main__":
    generate(500)
