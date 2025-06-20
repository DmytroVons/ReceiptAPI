from pydantic import BaseModel, constr
from typing import List, Literal
from decimal import Decimal
from datetime import datetime


class UserRegister(BaseModel):
    name: str
    username: constr(min_length=3)
    password: constr(min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class ProductInput(BaseModel):
    name: str
    price: Decimal
    quantity: Decimal

class ProductOutput(ProductInput):
    total: Decimal

class PaymentInput(BaseModel):
    type: Literal["cash", "cashless"]
    amount: Decimal

class PaymentOutput(PaymentInput):
    pass

class ReceiptCreate(BaseModel):
    products: List[ProductInput]
    payment: PaymentInput

class ReceiptOut(BaseModel):
    id: int
    products: List[ProductOutput]
    payment: PaymentOutput
    total: Decimal
    rest: Decimal
    created_at: datetime

    class Config:
        from_attributes = True

class ReceiptShort(BaseModel):
    id: int
    total: Decimal
    rest: Decimal
    payment_type: str
    payment_amount: Decimal
    created_at: datetime

    class Config:
        from_attributes = True

class PaginatedReceipts(BaseModel):
    total: int
    receipts: List[ReceiptShort]


