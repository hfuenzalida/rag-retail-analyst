"""Logfire observability wiring (optional in local dev)."""

import logging

import logfire

from app.core.config import Settings


def configure_logging(settings: Settings) -> None:
    import os

    if settings.logfire_ignore_no_config:
        os.environ.setdefault("LOGFIRE_IGNORE_NO_CONFIG", "1")

    logging.basicConfig(level=getattr(logging, settings.app_log_level.upper(), logging.INFO))

    if settings.logfire_token:
        logfire.configure(
            token=settings.logfire_token.get_secret_value(),
            environment=settings.logfire_environment or settings.app_env,
        )
        logfire.instrument_pydantic_ai()
    else:
        logging.getLogger(__name__).info(
            "Logfire not configured (APP_LOGFIRE_TOKEN unset); using span-only local tracing."
        )
