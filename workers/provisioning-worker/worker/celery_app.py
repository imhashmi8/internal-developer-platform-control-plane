from dotenv import load_dotenv
import os

from celery import Celery

load_dotenv("../../.env")

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "idp-worker",
    broker=redis_url,
    backend=redis_url,
    include=["worker.tasks"],
)

celery_app.conf.task_track_started = True
