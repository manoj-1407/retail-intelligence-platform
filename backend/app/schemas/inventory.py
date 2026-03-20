from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime


class InventoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    store_id: int
    quantity: int
    reorder_point: int
    updated_at: datetime | None = None


class AllocateRequest(BaseModel):
    product_id: int = Field(gt=0)
    store_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=50000)


class AllocateResponse(BaseModel):
    success: bool
    allocated: int
    remaining: int
    locked_ms: float
