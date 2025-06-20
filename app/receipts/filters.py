from fastapi import Query
from typing import Optional
from datetime import datetime

def get_receipt_filters(
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    min_total: Optional[float] = Query(None),
    max_total: Optional[float] = Query(None),
    payment_type: Optional[str] = Query(None),
    limit: int = Query(10, ge=1),
    offset: int = Query(0, ge=0),
):
    return {
        "date_from": date_from,
        "date_to": date_to,
        "min_total": min_total,
        "max_total": max_total,
        "payment_type": payment_type,
        "limit": limit,
        "offset": offset,
    }
