"""Benchmarks for Voice Runtime."""

from __future__ import annotations

import pytest

from cse.runtime.voice.runtime import VoiceRuntime
from cse.voice import register_voice_package, VoicePackage, VoiceMetadata
from pathlib import Path


@pytest.fixture
def mock_package():
    meta = VoiceMetadata(
        id="claire",
        name="Claire",
        version="1.0.0",
        author="Test",
        language="en",
        backend="dummy",
        sample_rate=24000,
        channels=1,
        description="Test",
        license="MIT"
    )
    return VoicePackage(metadata=meta, path=Path("/tmp/claire"))


def test_benchmark_runtime_initialization(benchmark):
    """Runtime initialization should be < 20ms."""
    def _run():
        runtime = VoiceRuntime()
        runtime.initialize()

    benchmark(_run)
    assert benchmark.stats["mean"] < 0.020, (
        f"Initialization mean {benchmark.stats['mean']:.4f}s exceeds 20ms target"
    )


def test_benchmark_load_metadata(benchmark, mock_package):
    runtime = VoiceRuntime()
    runtime.initialize()
    try:
        register_voice_package(mock_package)
    except Exception:
        pass

    def _run():
        runtime.load_voice("claire")

    benchmark(_run)


def test_benchmark_unload_metadata(benchmark, mock_package):
    runtime = VoiceRuntime()
    runtime.initialize()
    try:
        register_voice_package(mock_package)
    except Exception:
        pass

    def _run_clean():
        runtime.load_voice("claire")
        runtime.unload_voice()

    benchmark(_run_clean)
