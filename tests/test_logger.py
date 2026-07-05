"""Tests for the centralised logger."""

from __future__ import annotations

import pytest

from cse.core.logger import get_logger, setup_logger, _initialized


class TestLogger:
    """Logger unit tests."""

    def test_setup_logger_sets_initialized(self) -> None:
        setup_logger(debug=False)
        # After setup, get_logger should not raise
        logger = get_logger()
        assert logger is not None

    def test_setup_debug_mode(self) -> None:
        setup_logger(debug=True)
        logger = get_logger()
        assert logger is not None

    def test_logger_can_log_all_levels(self) -> None:
        setup_logger(debug=True)
        logger = get_logger()
        # These should not raise
        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warning message")
        logger.error("error message")
        logger.critical("critical message")
