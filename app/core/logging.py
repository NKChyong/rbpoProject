"""Logging configuration with request_id support."""

import contextvars
import logging
import sys
import uuid
from typing import Any

from fastapi import Request

# Context variable for request_id
request_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default=""
)


class RequestIdFilter(logging.Filter):
    """Add request_id to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add request_id to the record."""
        record.request_id = request_id_ctx.get("")
        return True


def setup_logging() -> None:
    """Configure application logging."""
    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - [request_id=%(request_id)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.addFilter(RequestIdFilter())

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    # Reduce noise from libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_request_id() -> str:
    """Get current request_id."""
    return request_id_ctx.get("")


def set_request_id(request_id: str) -> None:
    """Set request_id for current context."""
    request_id_ctx.set(request_id)


async def add_request_id(request: Request, call_next: Any) -> Any:
    """Middleware to add request_id to each request."""
    request_id = str(uuid.uuid4())
    set_request_id(request_id)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
