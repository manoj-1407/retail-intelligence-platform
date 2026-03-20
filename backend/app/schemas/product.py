from pydantic import BaseModel, ConfigDict, Field
from decimal import Decimal
from datetime import datetime


class ProductCreate(BaseModel):
    sku: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=255)
    category: str = Field(min_length=1, max_length=100)
    unit_cost: Decimal = Field(gt=0, decimal_places=2)
    unit_price: Decimal = Field(gt=0, decimal_places=2)


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    sku: str
    name: str
    category: str
    unit_cost: Decimal
    unit_price: Decimal
    created_at: datetime | None = None
