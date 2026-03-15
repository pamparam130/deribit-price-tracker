import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app
from app.core.database import Base, engine
from app.models.price import Price
from app.repositories.price_repository import PriceRepository
from app.api.dependencies import get_price_repository

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


def override_get_price_repository(db: Session = Depends(override_get_db)):
    return PriceRepository(db)


app.dependency_overrides[get_price_repository] = override_get_price_repository


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_get_prices_empty(client):
    response = client.get("/api/v1/prices/?ticker=btc_usd")
    assert response.status_code == 200
    assert response.json() == []


def test_get_prices_with_data(client, db_session):
    repo = PriceRepository(db_session)
    repo.create(ticker="btc_usd", price=50000.0)
    repo.create(ticker="btc_usd", price=51000.0)
    
    response = client.get("/api/v1/prices/?ticker=btc_usd")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["ticker"] == "btc_usd"
    assert data[0]["price"] == 50000.0


def test_get_latest_price(client, db_session):
    repo = PriceRepository(db_session)
    now = datetime.utcnow()
    earlier = now - timedelta(minutes=5)
    
    repo.create(ticker="btc_usd", price=50000.0, timestamp=earlier)
    latest = repo.create(ticker="btc_usd", price=51000.0, timestamp=now)
    
    response = client.get("/api/v1/prices/latest?ticker=btc_usd")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "btc_usd"
    assert data["price"] == 51000.0


def test_get_prices_by_date(client, db_session):
    repo = PriceRepository(db_session)
    now = datetime.utcnow()
    yesterday = now - timedelta(days=1)
    
    repo.create(ticker="btc_usd", price=50000.0, timestamp=yesterday)
    repo.create(ticker="btc_usd", price=51000.0, timestamp=now)
    
    response = client.get(
        f"/api/v1/prices/filter",
        params={
            "ticker": "btc_usd",
            "start_date": (yesterday - timedelta(minutes=1)).isoformat(),
            "end_date": (now + timedelta(minutes=1)).isoformat()
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_invalid_ticker(client):
    response = client.get("/api/v1/prices/?ticker=invalid")
    assert response.status_code == 400
    assert "Ticker must be either" in response.json()["detail"]


def test_invalid_date_format(client):
    response = client.get(
        "/api/v1/prices/filter",
        params={
            "ticker": "btc_usd",
            "start_date": "invalid-date",
            "end_date": "2024-01-01T00:00:00"
        }
    )
    assert response.status_code == 400
    assert "Invalid date format" in response.json()["detail"]