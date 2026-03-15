from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "deribit_tracker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.price_tasks"]
)

celery_app.conf.beat_schedule = {
    "fetch-prices-every-minute": {
        "task": "app.tasks.price_tasks.fetch_and_save_prices",
        "schedule": 60.0, 
    },
}

celery_app.conf.timezone = "UTC"