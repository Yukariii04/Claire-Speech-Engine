"""Benchmark: bootstrap startup time.

Target: < 300 ms (PRD-001 requirement).
Run with: pytest benchmarks/ --benchmark-only
"""

from __future__ import annotations

from unittest.mock import patch

from cse.runtime.bootstrap import bootstrap


def test_bootstrap_startup(benchmark) -> None:  # noqa: ANN001
    """Bootstrap must complete in under 300 ms."""

    def _run() -> None:
        with patch("sys.argv", ["cse"]):
            bootstrap()

    result = benchmark(_run)
    # pytest-benchmark tracks stats; assertion gives a hard fail at 300ms
    assert benchmark.stats["mean"] < 0.3, (
        f"Bootstrap mean time {benchmark.stats['mean']:.3f}s exceeds 300 ms target"
    )
