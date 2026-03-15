import aiohttp
import logging
from typing import Dict, Any
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class DeribitClient:
    def __init__(self):
        self.base_url = settings.DERIBIT_API_URL
    
    async def get_index_price(self, currency: str) -> Dict[str, Any]:
        currency_map = {
            'btc': 'btc_usd',
            'eth': 'eth_usd'
        }
        
        if currency not in currency_map:
            raise ValueError(f"Unsupported currency: {currency}")
        
        ticker = currency_map[currency]
        
        async with aiohttp.ClientSession() as session:
            try:
                params = {
                    'index_name': ticker
                }
                async with session.get(
                    f"{self.base_url}/public/get_index_price",
                    params=params
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('result'):
                            return {
                                'ticker': ticker,
                                'price': float(data['result']['index_price']),
                                'timestamp': datetime.fromtimestamp(
                                    data['result']['estimated_delivery_price'] / 1000
                                )
                            }
                    logger.error(f"Error fetching price for {ticker}: {response.status}")
                    return None
            except Exception as e:
                logger.error(f"Exception while fetching price for {ticker}: {e}")
                return None
    
    async def get_prices(self) -> Dict[str, Any]:
        tasks = []
        async with aiohttp.ClientSession() as session:
            for currency in ['btc', 'eth']:
                price_data = await self.get_index_price(currency)
                if price_data:
                    tasks.append(price_data)
            return tasks