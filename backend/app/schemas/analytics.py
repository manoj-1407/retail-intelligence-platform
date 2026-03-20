from pydantic import BaseModel


class RangeQueryResult(BaseModel):
    """Used by the /inventory/range endpoint only."""
    product_id:     int
    store_id_start: int
    store_id_end:   int
    total_quantity: int
    query_time_ms:  float

# AnalyticsSummary is intentionally not defined as a Pydantic response model
# because the /analytics/summary payload grows as new chart data is added.
# The endpoint returns a plain dict — FastAPI serialises it correctly and
# OpenAPI documents it as "object" which is accurate and honest.
