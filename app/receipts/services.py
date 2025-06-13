from typing import List
from decimal import Decimal
from app.schemas import ProductInput


def calculate_totals(products: List[ProductInput]):
    product_totals = []
    total_sum = Decimal("0.00")

    for item in products:
        total = item.price * item.quantity
        total_sum += total
        product_totals.append({
            "name": item.name,
            "price": item.price,
            "quantity": item.quantity,
            "total": total
        })

    return product_totals, total_sum
