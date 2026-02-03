from celery import Celery
import os

celery_app = Celery(
    "infra_insight_worker",
    broker=os.environ.get("REDIS_URL", "redis://redis:6379/0"),
    backend=os.environ.get("REDIS_URL", "redis://redis:6379/0"),
)
celery_app.autodiscover_tasks(["worker.tasks"])
celery_app.conf.timezone = "UTC"
