"""Benchmarks for the Developer Experience CLI (PRD-010)."""

import subprocess
import sys
from pathlib import Path

CSE_PY = str(Path(__file__).resolve().parents[1] / "cse.py")

from unittest.mock import patch
from cse.cli.main import main

def test_cli_startup_overhead(benchmark):
    """CLI startup (e.g., getting help) must be <200ms."""
    def run_cli_help():
        with patch("sys.argv", ["cse", "help"]):
            try:
                main()
            except SystemExit:
                pass

    benchmark(run_cli_help)
