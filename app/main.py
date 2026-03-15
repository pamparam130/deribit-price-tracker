from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.endpoints import prices
from app.core.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prices.router, prefix=settings.API_V1_PREFIX, tags=["prices"])


@app.get("/")
async def root():
    return {
        "message": "Deribit Price Tracker API",
        "docs": "/docs",
        "endpoints": {
            "get_prices": f"{settings.API_V1_PREFIX}/prices/?ticker=btc_usd",
            "latest_price": f"{settings.API_V1_PREFIX}/prices/latest?ticker=btc_usd",
            "filter_by_date": f"{settings.API_V1_PREFIX}/prices/filter?ticker=btc_usd&start_date=2024-01-01T00:00:00&end_date=2024-01-02T00:00:00"
        }
    }