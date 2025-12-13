from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class CartItemIn(BaseModel):
    productId: str
    quantity: int

class CartItemOut(BaseModel):
    productId: str
    quantity: int

from datetime import datetime

class CartOut(BaseModel):
    userId: str
    items: List[CartItemOut]
    updatedAt: Optional[datetime] = None
