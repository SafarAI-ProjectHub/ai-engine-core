import logging
import os
import sys
import uuid
from contextvars import ContextVar

from fastapi import Request


# Context variable to store correlation ID per request/task
_correlation_id_ctx: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def get_correlation_id() -> str | None:
    """Return the current correlation ID (if any)."""
    return _correlation_id_ctx.get()


def set_correlation_id(correlation_id: str | None) -> None:
    """Set the correlation ID in the current context."""
    _correlation_id_ctx.set(correlation_id)


class CorrelationIdFilter(logging.Filter):
    """Logging filter that injects the current correlation ID into log records."""

    def filter(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        record.correlation_id = get_correlation_id() or "-"
        return True


def configure_logging() -> None:
    """
    Configure application-wide logging.

    - Root level defaults to INFO, overridable via LOG_LEVEL.
    - Logs go to stdout by default.
    - Optional rotating file handler when LOG_TO_FILE=true.
    """
    log_level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_name, logging.INFO)

    root_logger = logging.getLogger()
    # Avoid adding handlers multiple times in reload scenarios
    if root_logger.handlers:
        return

    root_logger.setLevel(log_level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(correlation_id)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    correlation_filter = CorrelationIdFilter()

    # Console / stdout handler (always enabled)
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.addFilter(correlation_filter)
    root_logger.addHandler(console_handler)

    # Optional rotating file handler
    if os.getenv("LOG_TO_FILE", "false").lower() == "true":
        from logging.handlers import RotatingFileHandler

        log_file = os.getenv("LOG_FILE", "logs/app.log")
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=int(os.getenv("LOG_FILE_MAX_BYTES", str(10 * 1024 * 1024))),
            backupCount=int(os.getenv("LOG_FILE_BACKUP_COUNT", "5")),
        )
        file_handler.setFormatter(formatter)
        file_handler.addFilter(correlation_filter)
        root_logger.addHandler(file_handler)


def get_logger(name: str | None = None) -> logging.Logger:
    """Helper to get a logger with the application configuration."""
    return logging.getLogger(name)


async def logging_middleware(request: Request, call_next):
    """
    FastAPI middleware to:
    - Generate/extract a correlation ID
    - Log request start and end with timing and status
    """
    # Extract or create correlation ID
    incoming_cid = request.headers.get("X-Request-ID") or request.headers.get("X-Correlation-ID")
    correlation_id = incoming_cid or str(uuid.uuid4())
    set_correlation_id(correlation_id)

    logger = get_logger("request")
    client_host = request.client.host if request.client else "-"

    logger.info(
        "Request start %s %s from %s",
        request.method,
        request.url.path,
        client_host,
    )

    try:
        import time

        start_time = time.time()
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000

        logger.info(
            "Request end %s %s -> %s (%.2f ms)",
            request.method,
            request.url.path,
            getattr(response, "status_code", "-"),
            duration_ms,
        )

        # Propagate correlation ID back to the client
        response.headers["X-Request-ID"] = correlation_id
        return response
    except Exception:
        logger.exception(
            "Unhandled exception while processing %s %s",
            request.method,
            request.url.path,
        )
        raise
    finally:
        # Clear correlation ID for this context
        set_correlation_id(None)


