from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal
from pydantic import BaseModel, Field, EmailStr


class RawOrderItem(BaseModel):
    name: str = Field(..., min_length=2, max_length=200, description="Название товара")
    category: str = Field(..., min_length=2, max_length=200, description="Название категории")
    quantity: int = Field(..., gt=0, le=1000, description="Количество")
    price: Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2),]
    cost: Annotated[Decimal, Field(gt=0, max_digits=10, decimal_places=2)]

class RawOrder(BaseModel):
    client_name: str = Field(..., min_length=2, max_length=200)
    client_surname: str = Field(..., min_length=2, max_length=200)
    client_email: EmailStr
    city: str = Field(..., max_length=50)
    items_list: list[RawOrderItem]
    created_at: datetime
    status: Literal['new', 'paid', 'delivered', 'cancelled'] = 'paid'