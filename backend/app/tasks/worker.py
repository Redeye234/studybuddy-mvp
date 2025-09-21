import os
from celery import Celery


broker = os.getenv("REDIS_URL", "redis://localhost:6379/0")
backend = broker

celery_app = Celery("studybuddy", broker=broker, backend=backend)
celery_app.autodiscover_tasks(["backend.app.tasks"])  # package path for tasks


@celery_app.task
def ping():
    return "pong"

