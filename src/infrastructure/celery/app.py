"""
CrowdIQ — Celery Application
"""
from __future__ import annotations

from celery import Celery

from src.shared.configs.settings import settings

celery_app = Celery(
    "crowdiq",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["src.infrastructure.celery.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
)
