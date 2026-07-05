"""Tests for CLI argument handling."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


CSE_PY = str(Path(__file__).resolve().parents[1] / "cse.py")


class TestCLI:
    """CLI integration tests."""

    def test_help_flag(self) -> None:
        """--help should print usage and exit 0."""
        result = subprocess.run(
            [sys.executable, CSE_PY, "--help"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "usage" in result.stdout.lower() or "Claire" in result.stdout

    def test_version_flag(self) -> None:
        """--version should print version string and exit 0."""
        result = subprocess.run(
            [sys.executable, CSE_PY, "--version"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "0.1.0" in result.stdout

    def test_debug_flag(self) -> None:
        """--debug should complete without error."""
        result = subprocess.run(
            [sys.executable, CSE_PY, "--debug"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0

    def test_default_run(self) -> None:
        """Running without flags should print the startup banner."""
        result = subprocess.run(
            [sys.executable, CSE_PY],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "Claire Speech Engine" in result.stdout
        assert "Runtime Ready" in result.stdout
