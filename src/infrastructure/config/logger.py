"""
CrowdIQ — Centralized Logging Configuration
"""
import logging
import sys
from src.infrastructure.config.settings import settings

def setup_logging() -> None:
    """Configure the application logging."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    # Set the global logging format
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    
    # Configure the root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # You can set specific log levels for noisy third-party libraries if needed
    # logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    # logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
