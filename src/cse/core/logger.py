"""Centralised logger — loguru-based, colorized, timestamped."""

from __future__ import annotations

import sys

from loguru import logger as _loguru_logger


# ponytail: single global flag, no class wrapping needed
_initialized: bool = False


def setup_logger(*, debug: bool = False) -> None:
    """Configure the global loguru logger.

    Removes default sinks and adds a single colorized stderr sink.

    Args:
        debug: If *True*, set level to DEBUG; otherwise INFO.
    """
    global _initialized

    _loguru_logger.remove()  # clear default handler
    level = "DEBUG" if debug else "INFO"
    _loguru_logger.add(
        sys.stderr,
        level=level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — "
            "<level>{message}</level>"
        ),
        colorize=True,
    )
    _initialized = True


def get_logger() -> _loguru_logger.__class__:
    """Return the configured loguru logger.

    Every module must use this instead of ``print()``.

    Raises:
        RuntimeError: If called before ``setup_logger()``.
    """
    if not _initialized:
        raise RuntimeError("Logger not initialised — call bootstrap() first.")
    return _loguru_logger
