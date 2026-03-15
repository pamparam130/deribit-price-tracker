from pydantic import BaseModel
from datetime import datetime


class PriceBase(BaseModel):
    ticker: str
    price: float
    timestamp: datetime


class PriceCreate(PriceBase):
    pass


class PriceResponse(PriceBase):
    id: int
    
    class Config:
        from_attributes = True


class PriceLatestResponse(BaseModel):
    ticker: str
    price: float
    timestamp: datetime