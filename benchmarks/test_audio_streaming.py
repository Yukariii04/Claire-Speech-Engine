"""Benchmarks for Audio Streaming Pipeline (PRD-006 §15)."""

from __future__ import annotations

import uuid
import pytest

from cse.streaming.audio.controller import StreamController
from cse.streaming.audio.frame import AudioFrame


@pytest.fixture
def valid_frame():
    return AudioFrame(
        uuid=uuid.uuid4(),
        timestamp_ms=0.0,
        sample_rate=24000,
        channels=1,
        sample_format="PCM_16",
        samples=b"\x00\x00",
        duration_ms=10.0
    )


def test_benchmark_push_pop(benchmark, valid_frame):
    """Benchmark pushing and popping 1000 frames."""
    controller = StreamController(max_buffer_size=1000)
    
    def _run():
        controller.create_stream()
        for _ in range(1000):
            controller.push_frame(valid_frame)
            
        for _ in range(1000):
            controller.pop_frame()

    benchmark(_run)
    assert benchmark.stats["mean"] < 0.020, (
        f"1000 push/pop mean {benchmark.stats['mean']:.4f}s exceeds 20ms target"
    )

def test_benchmark_streams(benchmark, valid_frame):
    """Benchmark creating 100 streams."""
    controller = StreamController()
    
    def _run():
        for _ in range(100):
            controller.create_stream()
            controller.close()
            
    benchmark(_run)
