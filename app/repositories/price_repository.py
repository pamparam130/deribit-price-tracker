from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.price import Price


class PriceRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, ticker: str, price: float, timestamp: Optional[datetime] = None) -> Price:
        if timestamp is None:
            timestamp = datetime.utcnow()
        db_price = Price(
            ticker=ticker,
            price=price,
            timestamp=timestamp
        )
        self.db.add(db_price)
        self.db.commit()
        self.db.refresh(db_price)
        return db_price
    
    def get_by_ticker(self, ticker: str) -> List[Price]:
        return self.db.query(Price).filter(Price.ticker == ticker).all()
    
    def get_latest_by_ticker(self, ticker: str) -> Optional[Price]:
        return self.db.query(Price)\
            .filter(Price.ticker == ticker)\
            .order_by(Price.timestamp.desc())\
            .first()
    
    def get_by_ticker_and_date_range(
        self, 
        ticker: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> List[Price]:
        return self.db.query(Price)\
            .filter(
                and_(
                    Price.ticker == ticker,
                    Price.timestamp >= start_date,
                    Price.timestamp <= end_date
                )
            )\
            .order_by(Price.timestamp.desc())\
            .all()
    
    def create_bulk(self, prices_data: List[dict]) -> List[Price]:
        db_prices = [Price(**data) for data in prices_data]
        self.db.add_all(db_prices)
        self.db.commit()
        for price in db_prices:
            self.db.refresh(price)
        return db_prices