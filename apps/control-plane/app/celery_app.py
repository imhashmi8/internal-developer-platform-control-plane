from celery import Celery

from app.core import settings

celery_app = Celery(broker=settings.redis_url)
