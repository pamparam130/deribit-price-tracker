from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import datetime

from app.schemas.price import PriceResponse, PriceLatestResponse
from app.api.dependencies import get_price_repository, validate_ticker, parse_date
from app.repositories.price_repository import PriceRepository

router = APIRouter()


@router.get("/prices/", response_model=List[PriceResponse])
async def get_prices(
    ticker: str = Depends(validate_ticker),
    repository: PriceRepository = Depends(get_price_repository)
):
    prices = repository.get_by_ticker(ticker)
    return prices


@router.get("/prices/latest", response_model=PriceLatestResponse)
async def get_latest_price(
    ticker: str = Depends(validate_ticker),
    repository: PriceRepository = Depends(get_price_repository)
):
    price = repository.get_latest_by_ticker(ticker)
    if not price:
        raise HTTPException(
            status_code=404,
            detail=f"No prices found for ticker {ticker}"
        )
    return price


@router.get("/prices/filter", response_model=List[PriceResponse])
async def get_prices_by_date(
    ticker: str = Depends(validate_ticker),
    start_date: str = Query(..., description="Начальная дата (ISO format)"),
    end_date: str = Query(..., description="Конечная дата (ISO format)"),
    repository: PriceRepository = Depends(get_price_repository)
):
    start = parse_date(start_date)
    end = parse_date(end_date)
    
    if start > end:
        raise HTTPException(
            status_code=400,
            detail="start_date must be before end_date"
        )
    
    prices = repository.get_by_ticker_and_date_range(ticker, start, end)
    return prices
