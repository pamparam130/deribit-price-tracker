import asyncio
import logging
from celery import shared_task
from datetime import datetime

from app.core.database import SessionLocal
from app.repositories.price_repository import PriceRepository
from app.services.deribit_client import DeribitClient

logger = logging.getLogger(__name__)


def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@shared_task(name="app.tasks.price_tasks.fetch_and_save_prices")
def fetch_and_save_prices():
    logger.info("Starting fetch_and_save_prices task")
    
    async def _fetch_and_save():
        client = DeribitClient()
        prices_data = await client.get_prices()
        if not prices_data:
            logger.warning("No price data received from Deribit")
            return
        
        db = SessionLocal()
        try:
            repository = PriceRepository(db)
            
            saved_prices = []
            for price_data in prices_data:
                price = repository.create(
                    ticker=price_data['ticker'],
                    price=price_data['price'],
                    timestamp=price_data['timestamp']
                )
                saved_prices.append(price)
                logger.info(f"Saved price for {price.ticker}: {price.price}")
            
            return f"Saved {len(saved_prices)} prices"
        finally:
            db.close()
    
    return run_async(_fetch_and_save())