from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from enum import Enum

class PaymentType(str, Enum):
    cash = "cash"
    cashless = "cashless"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)

    receipts = relationship("Receipt", back_populates="user")

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    total = Column(Numeric(12, 2), nullable=False)
    payment_type = Column(Enum(PaymentType), nullable=False)
    payment_amount = Column(Numeric(12, 2), nullable=False)
    rest = Column(Numeric(12, 2), nullable=False)

    user = relationship("User", back_populates="receipts")
    products = relationship("Product", back_populates="receipt", cascade="all, delete")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id"))
    name = Column(String, nullable=False)
    price = Column(Numeric(12, 2), nullable=False)
    quantity = Column(Numeric(12, 2), nullable=False)
    total = Column(Numeric(12, 2), nullable=False)

    receipt = relationship("Receipt", back_populates="products")
