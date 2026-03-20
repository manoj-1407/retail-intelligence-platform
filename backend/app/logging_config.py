"""
Structured logging setup using structlog.

Usage in any module:
    from app.logging_config import get_logger
    log = get_logger(__name__)
    log.info("event", user_id=123, action="login")

Output (JSON in production, coloured in dev):
    {"event": "event", "user_id": 123, "action": "login",
     "timestamp": "2025-01-01T00:00:00Z", "level": "info"}
"""
import logging
import os
import structlog


def setup_logging() -> None:
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Standard library logging — captures uvicorn / sqlalchemy logs too
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level, logging.INFO),
    )

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if os.getenv("ENV", "dev") == "production":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__):
    """Return a structlog logger bound to the given module name."""
    return structlog.get_logger(name)
