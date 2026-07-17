"""
infrastructure/logger.py
────────────────────────
Structured logging via structlog.
Import `log` from here everywhere in the application.

Usage:
    from app.infrastructure.logger import log

    log.info("ingestion.started", doc_id=doc_id, doc_type=doc_type)
    log.error("ingestion.failed", doc_id=doc_id, stage="parse", error=str(e))
"""
import logging
import sys

import structlog

from app.config import settings


def _configure_logging() -> None:
    """Configure structlog with appropriate processors for the environment."""

    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
    ]

    if settings.is_production:
        # JSON output for log aggregators (Render, etc.)
        processors = shared_processors + [
            structlog.processors.ExceptionDictTransformer(),
            structlog.processors.JSONRenderer(),
        ]
    else:
        # Human-readable console output for development
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(colors=True),
        ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.DEBUG if not settings.is_production else logging.INFO
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )


_configure_logging()

log = structlog.get_logger("kite")
