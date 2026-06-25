"""
CrowdIQ — Background Tasks (Celery)
"""
from __future__ import annotations

import asyncio

from src.infrastructure.output.adapter.celery.app import celery_app


@celery_app.task(name="tasks.send_email_notification")
def send_email_notification(to_email: str, subject: str, body: str) -> None:
    """Placeholder — wire up an SMTP / SendGrid provider here."""
    print(f"[EMAIL] To: {to_email} | Subject: {subject}")


@celery_app.task(name="tasks.run_ai_analysis")
def run_ai_analysis(prediction_id: str) -> None:
    """Trigger AI analysis for a prediction asynchronously."""
    from src.infrastructure.output.adapter.openai.client import chat_completion  # lazy import

    async def _analyse() -> None:
        result = await chat_completion(
            system_prompt="You are a prediction analysis assistant.",
            user_prompt=f"Analyse prediction {prediction_id} for credibility and sentiment.",
        )
        print(f"[AI] prediction={prediction_id} result={result[:120]}")

    asyncio.run(_analyse())


@celery_app.task(name="tasks.resolve_expired_predictions")
def resolve_expired_predictions() -> None:
    """Scheduled task — find expired predictions and mark them AWAITING_RESOLUTION."""
    print("[TASKS] Checking for expired predictions…")
