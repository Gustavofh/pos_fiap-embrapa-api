from pydantic import BaseModel
from typing import Optional

class ProductFilter(BaseModel):
    id: Optional[str] = None
    product: Optional[str] = None
    minQuantity: Optional[int] = None
    maxQuantity: Optional[int] = None