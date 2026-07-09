"""
CrowdIQ — Email Service
Handles sending transactional emails (OTP, password reset, welcome, etc.)
via the Celery background task queue, with optional HTML templates.
"""
from __future__ import annotations

import os
from string import Template

from src.infrastructure.celery.tasks import send_email_notification

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")


class EmailService:
    """Centralized email sending logic."""

    @staticmethod
    def _render_template(template_name: str, **context) -> str:
        path = os.path.join(TEMPLATES_DIR, template_name)
        with open(path, "r", encoding="utf-8") as f:
            template = Template(f.read())
        return template.safe_substitute(**context)

    @classmethod
    def send_otp_email(cls, to_email: str, otp: str) -> None:
        body = f"Your OTP code is: {otp}. It is valid for 5 minutes."
        send_email_notification.delay(
            to_email=to_email,
            subject="Your CrowdIQ OTP Code",
            body=body,
        )

    @classmethod
    def send_reset_otp_email(cls, to_email: str, otp: str) -> None:
        body = (
            f"You requested a password reset. Your OTP is: {otp}.\n"
            f"It is valid for 5 minutes. Do not share it with anyone."
        )
        send_email_notification.delay(
            to_email=to_email,
            subject="CrowdIQ Password Reset OTP",
            body=body,
        )

    @classmethod
    def send_welcome_email(cls, to_email: str, username: str) -> None:
        body = f"Welcome to CrowdIQ, {username}! Your account has been created."
        send_email_notification.delay(
            to_email=to_email,
            subject="Welcome to CrowdIQ",
            body=body,
        )

    @classmethod
    def send_html_email(cls, to_email: str, subject: str, template_name: str, **context) -> None:
        """Send an email rendered from an HTML template file."""
        body = cls._render_template(template_name, **context)
        send_email_notification.delay(
            to_email=to_email,
            subject=subject,
            body=body,
        )
