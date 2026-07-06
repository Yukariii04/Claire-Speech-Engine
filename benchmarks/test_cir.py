"""Benchmark: CIR builder, validator, serializer, deserializer.

Targets (PRD §19/§22):
  - 100-word paragraph build: < 5 ms
  - 1000 builds: < 1 second total
Run with: pytest benchmarks/test_cir.py --benchmark-only
"""

from __future__ import annotations

from cse.language.cir.builder import build_cir
from cse.language.cir.serializer import deserialize, serialize
from cse.language.cir.validator import validate

# 100-word paragraph for benchmarking.
_PARAGRAPH = " ".join(["The quick brown fox jumps over the lazy dog."] * 11)  # ~99 words + structure
_SIMPLE = "I really missed you."


def test_benchmark_builder(benchmark) -> None:  # noqa: ANN001
    """build_cir on a 100-word paragraph must complete in < 5 ms."""
    result = benchmark(build_cir, _PARAGRAPH)
    assert result is not None
    assert benchmark.stats["mean"] < 0.005, (
        f"Builder mean {benchmark.stats['mean']:.4f}s exceeds 5 ms target"
    )


def test_benchmark_validator(benchmark) -> None:  # noqa: ANN001
    """Validator should be fast on a pre-built document."""
    doc = build_cir(_PARAGRAPH)
    benchmark(validate, doc)


def test_benchmark_serializer(benchmark) -> None:  # noqa: ANN001
    """Serializer should be fast."""
    doc = build_cir(_PARAGRAPH)
    benchmark(serialize, doc)


def test_benchmark_deserializer(benchmark) -> None:  # noqa: ANN001
    """Deserializer should be fast."""
    doc = build_cir(_PARAGRAPH)
    json_str = serialize(doc)
    result = benchmark(deserialize, json_str)
    assert result is not None


def test_benchmark_1000_builds(benchmark) -> None:  # noqa: ANN001
    """1000 CIR builds must complete in < 1 second (PRD §22)."""

    def _run() -> None:
        for _ in range(1000):
            build_cir(_SIMPLE)

    benchmark(_run)
    assert benchmark.stats["mean"] < 1.0, (
        f"1000-build mean {benchmark.stats['mean']:.3f}s exceeds 1 second target"
    )
