from celery import Celery
from core.config.celery import BROKER_URL


celery = Celery(
    broker=BROKER_URL,
    include=[
        "apps.auth.tasks"
    ]
) 


