from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Literal


class ShipmentCreate(BaseModel):
    product_id: int = Field(gt=0)
    store_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=100000)


class ShipmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    store_id: int
    quantity: int
    status: str
    shipped_at: datetime | None = None
    delivered_at: datetime | None = None
    created_at: datetime | None = None
