"""Benchmarks for Performance Compiler (PRD §19 & §23).

Run with: pytest benchmarks/test_perf_compiler.py --benchmark-only
"""

from __future__ import annotations

from cse.language.cir import build_cir
from cse.performance.compiler import compile_performance
from cse.performance.compiler.serializer import deserialize_timeline, serialize_timeline
from cse.performance.compiler.validator import validate_timeline

_PARAGRAPH = " ".join(["The quick brown fox jumps over the lazy dog."] * 11)
_SIMPLE = "Hello."


def test_benchmark_compile_performance(benchmark) -> None:  # noqa: ANN001
    """Compile 100 words -> Timeline in < 2 ms (PRD §19)."""
    cir = build_cir(_PARAGRAPH)
    result = benchmark(compile_performance, cir)
    assert result is not None
    assert benchmark.stats["mean"] < 0.002, (
        f"Compile mean {benchmark.stats['mean']:.4f}s exceeds 2 ms target"
    )


def test_benchmark_validate_timeline(benchmark) -> None:  # noqa: ANN001
    cir = build_cir(_PARAGRAPH)
    tl = compile_performance(cir)
    benchmark(validate_timeline, tl)


def test_benchmark_serialize_timeline(benchmark) -> None:  # noqa: ANN001
    cir = build_cir(_PARAGRAPH)
    tl = compile_performance(cir)
    benchmark(serialize_timeline, tl)


def test_benchmark_deserialize_timeline(benchmark) -> None:  # noqa: ANN001
    cir = build_cir(_PARAGRAPH)
    tl = compile_performance(cir)
    json_str = serialize_timeline(tl)
    benchmark(deserialize_timeline, json_str)


def test_benchmark_1000_timelines(benchmark) -> None:  # noqa: ANN001
    """1000 timelines compiled in < 1 second (PRD §23)."""
    cir = build_cir(_SIMPLE)

    def _run() -> None:
        for _ in range(1000):
            compile_performance(cir)

    benchmark(_run)
    assert benchmark.stats["mean"] < 1.0, (
        f"1000 timelines mean {benchmark.stats['mean']:.3f}s exceeds 1s target"
    )
