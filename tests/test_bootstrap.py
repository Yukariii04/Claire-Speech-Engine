"""Tests for runtime bootstrap and shutdown."""

from __future__ import annotations

import sys
from unittest.mock import patch

import pytest

from cse.config.manager import get_config, _set_config
from cse.core.logger import get_logger
from cse.core.registry import get_registry, _set_registry
from cse.runtime.bootstrap import bootstrap, shutdown


class TestBootstrap:
    """Runtime bootstrap tests."""

    def test_bootstrap_runs_cleanly(self) -> None:
        """bootstrap() should complete without errors when given no CLI args."""
        with patch("sys.argv", ["cse"]):
            bootstrap()

        # All singletons should now be accessible
        assert get_config().is_loaded
        assert get_logger() is not None
        assert get_registry() is not None

    def test_bootstrap_debug_flag(self) -> None:
        """--debug flag should not crash the bootstrap."""
        with patch("sys.argv", ["cse", "--debug"]):
            bootstrap()

        assert get_config().get("runtime.debug") is not None

    def test_shutdown(self) -> None:
        """shutdown() should complete cleanly."""
        with patch("sys.argv", ["cse"]):
            bootstrap()
            shutdown()

    def test_banner_output(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Banner should contain the engine name and version."""
        with patch("sys.argv", ["cse"]):
            bootstrap()

        captured = capsys.readouterr().out
        assert "Claire Speech Engine" in captured
        assert "Version 0.1.0" in captured
        assert "Configuration Loaded" in captured
        assert "Logger Initialized" in captured
        assert "Module Registry Initialized" in captured
        assert "Runtime Ready" in captured
