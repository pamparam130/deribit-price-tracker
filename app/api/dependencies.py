from typing import Annotated
from fastapi import Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.database import get_db
from app.repositories.price_repository import PriceRepository


def get_price_repository(db: Session = Depends(get_db)) -> PriceRepository:
    return PriceRepository(db)


def validate_ticker(ticker: str = Query(..., description="Тикер валюты (btc_usd или eth_usd)")) -> str:
    if ticker not in ["btc_usd", "eth_usd"]:
        raise HTTPException(
            status_code=400,
            detail="Ticker must be either 'btc_usd' or 'eth_usd'"
        )
    return ticker


def parse_date(date_str: str) -> datetime:
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        )