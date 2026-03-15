import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.repositories.price_repository import PriceRepository
from app.models.price import Price

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def repository(db_session):
    return PriceRepository(db_session)


def test_create_price(repository):
    ticker = "btc_usd"
    price_value = 50000.0
    
    result = repository.create(ticker=ticker, price=price_value)
    
    assert result.ticker == ticker
    assert result.price == price_value
    assert result.id is not None
    assert result.timestamp is not None


def test_get_by_ticker(repository):
    repository.create(ticker="btc_usd", price=50000.0)
    repository.create(ticker="btc_usd", price=51000.0)
    repository.create(ticker="eth_usd", price=3000.0)
    
    btc_prices = repository.get_by_ticker("btc_usd")
    eth_prices = repository.get_by_ticker("eth_usd")
    
    assert len(btc_prices) == 2
    assert len(eth_prices) == 1


def test_get_latest_by_ticker(repository):
    now = datetime.utcnow()
    earlier = now - timedelta(minutes=5)

    price1 = repository.create(ticker="btc_usd", price=50000.0, timestamp=earlier)
    price2 = repository.create(ticker="btc_usd", price=51000.0, timestamp=now)
    
    latest = repository.get_latest_by_ticker("btc_usd")
    
    assert latest.id == price2.id
    assert latest.price == 51000.0


def test_get_by_ticker_and_date_range(repository):
    now = datetime.utcnow()
    day_before = now - timedelta(days=1)
    two_days_before = now - timedelta(days=2)

    repository.create(ticker="btc_usd", price=50000.0, timestamp=two_days_before)
    repository.create(ticker="btc_usd", price=51000.0, timestamp=day_before)
    repository.create(ticker="btc_usd", price=52000.0, timestamp=now)
    
    filtered = repository.get_by_ticker_and_date_range(
        "btc_usd",
        day_before - timedelta(minutes=1),
        now + timedelta(minutes=1)
    )
    
    assert len(filtered) == 2 
    assert filtered[0].price == 52000.0