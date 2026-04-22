from typing import List
from pydantic import BaseModel, ConfigDict, Field

class ProductBase(BaseModel):
    name: str
    description: str | None = None
    price: float
    category: str
    rating: float = Field(default=0.0)

class ProductOut(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class ProductPagination(BaseModel):
    items: List[ProductOut]
    total: int
    page:int
    size:int
