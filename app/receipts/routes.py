from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.schemas import ReceiptCreate, ReceiptOut
from app.models import Receipt, Product
from app.auth.utils import get_current_user
from app.receipts.services import calculate_totals
from decimal import Decimal
from .filters import get_receipt_filters
from app.schemas import PaginatedReceipts
from sqlalchemy import select, func, and_

router = APIRouter(prefix="/receipts", tags=["Receipts"])


@router.post("/", response_model=ReceiptOut)
async def create_receipt(
    receipt_data: ReceiptCreate,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user)
):
    product_totals, total_sum = calculate_totals(receipt_data.products)
    rest = receipt_data.payment.amount - total_sum

    receipt = Receipt(
        user_id=current_user.id,
        total=total_sum,
        rest=rest,
        payment_type=receipt_data.payment.type,
        payment_amount=receipt_data.payment.amount
    )
    session.add(receipt)
    await session.flush()

    for item in product_totals:
        product = Product(
            receipt_id=receipt.id,
            name=item["name"],
            price=item["price"],
            quantity=item["quantity"],
            total=item["total"]
        )
        session.add(product)

    await session.commit()
    await session.refresh(receipt)

    return {
        "id": receipt.id,
        "products": product_totals,
        "payment": receipt_data.payment,
        "total": total_sum,
        "rest": rest,
        "created_at": receipt.created_at
    }


@router.get("/", response_model=PaginatedReceipts)
async def list_receipts(
    filters: dict = Depends(get_receipt_filters),
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user),
):
    conditions = [Receipt.user_id == current_user.id]

    if filters["date_from"]:
        conditions.append(Receipt.created_at >= filters["date_from"])
    if filters["date_to"]:
        conditions.append(Receipt.created_at <= filters["date_to"])
    if filters["min_total"]:
        conditions.append(Receipt.total >= filters["min_total"])
    if filters["max_total"]:
        conditions.append(Receipt.total <= filters["max_total"])
    if filters["payment_type"]:
        conditions.append(Receipt.payment_type == filters["payment_type"])

    stmt = (
        select(Receipt)
        .where(and_(*conditions))
        .offset(filters["offset"])
        .limit(filters["limit"])
        .order_by(Receipt.created_at.desc())
    )

    total_stmt = select(func.count()).select_from(Receipt).where(and_(*conditions))

    result = await session.execute(stmt)
    receipts = result.scalars().all()

    total_result = await session.execute(total_stmt)
    total = total_result.scalar()

    return {
        "total": total,
        "receipts": receipts
    }


@router.get("/{receipt_id}", response_model=ReceiptOut)
async def get_receipt_by_id(
    receipt_id: int,
    session: AsyncSession = Depends(get_session),
    current_user = Depends(get_current_user)
):
    stmt = select(Receipt).where(Receipt.id == receipt_id, Receipt.user_id == current_user.id)
    result = await session.execute(stmt)
    receipt = result.scalar()

    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    products_stmt = select(Product).where(Product.receipt_id == receipt.id)
    products = (await session.execute(products_stmt)).scalars().all()

    return {
        "id": receipt.id,
        "products": products,
        "payment": {
            "type": receipt.payment_type,
            "amount": receipt.payment_amount,
        },
        "total": receipt.total,
        "rest": receipt.rest,
        "created_at": receipt.created_at,
    }


@router.get("/public/{receipt_id}/", response_class=PlainTextResponse)
async def get_receipt_text(
    receipt_id: int,
    line_width: int = Query(32, ge=10, le=100),
    session: AsyncSession = Depends(get_session)
):
    stmt = select(Receipt).where(Receipt.id == receipt_id)
    result = await session.execute(stmt)
    receipt = result.scalar()

    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    products = (await session.execute(select(Product).where(Product.receipt_id == receipt.id))).scalars().all()

    def center(text): return text.center(line_width)
    def line(char='='): return char * line_width

    rows = [center("ФОП Джонсонюк Борис"), line()]
    for p in products:
        line1 = f"{p.quantity:.2f} x {int(p.price):,}".replace(",", " ")
        line2 = f"{p.name} {int(p.total):,}".replace(",", " ")
        rows += [line1, line2]

    rows += [
        line('-'),
        f"СУМА {int(receipt.total):,}".replace(",", " "),
        f"{'Картка' if receipt.payment_type == 'cashless' else 'Готівка'} {int(receipt.payment_amount):,}".replace(",", " "),
        f"Решта {int(receipt.rest):,}".replace(",", " "),
        line(),
        receipt.created_at.strftime("%d.%m.%Y %H:%M"),
        "Дякуємо за покупку!",
    ]

    return "\n".join(rows)
