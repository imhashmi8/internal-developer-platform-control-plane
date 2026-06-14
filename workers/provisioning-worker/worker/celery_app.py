import os

from celery import Celery

try:
    from dotenv import load_dotenv

    load_dotenv("../../.env")
except ImportError:
    # python-dotenv is a convenience for local runs; env vars may also be
    # supplied directly (e.g. via `uv run --env-file` or the process env).
    pass

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "idp-worker",
    broker=redis_url,
    backend=redis_url,
    include=["worker.tasks"],
)

celery_app.conf.task_track_started = True
