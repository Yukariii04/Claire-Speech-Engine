"""Benchmarks for Kokoro Backend (PRD-008 §13)."""

from __future__ import annotations

import uuid
from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pytest

from cse.backends.kokoro.backend import KokoroBackend
from cse.backends.kokoro.config import KokoroConfig
from cse.performance.compiler.events import EVENT_TOKEN, PerformanceEvent
from cse.performance.compiler.timeline import PerformanceTimeline, PerformanceMetadata


@pytest.fixture
def simple_timeline():
    events = (
        PerformanceEvent(
            uuid=uuid.uuid4(),
            timestamp_ms=0,
            event_type=EVENT_TOKEN,
            parameters={"token": "Hello world, this is a test sentence."},
        ),
    )
    return PerformanceTimeline(
        uuid=uuid.uuid4(),
        version="1.0.0",
        events=events,
        metadata=PerformanceMetadata(),
    )


MODEL_PATH = Path("models/kokoro/kokoro-v1.0.onnx")
VOICES_PATH = Path("models/kokoro/voices-v1.0.bin")

kokoro_model = pytest.mark.skipif(
    not (MODEL_PATH.exists() and VOICES_PATH.exists()),
    reason="Kokoro model files not found.",
)


@kokoro_model
def test_benchmark_kokoro_synthesis(benchmark, simple_timeline, tmp_path):
    """Benchmark Kokoro single sentence synthesis."""
    config = KokoroConfig(
        output_dir=str(tmp_path),
        model_path=MODEL_PATH,
        voices_path=VOICES_PATH,
    )
    backend = KokoroBackend(config=config)
    backend.initialize()
    backend.load_voice("af_heart")

    def _run():
        backend.synthesize(simple_timeline)

    benchmark(_run)
    backend.shutdown()


def test_benchmark_converter(benchmark, simple_timeline):
    """Benchmark timeline-to-text conversion."""
    from cse.backends.kokoro.converter import timeline_to_text

    def _run():
        for _ in range(1000):
            timeline_to_text(simple_timeline)

    benchmark(_run)


def test_benchmark_mocked_synthesis(benchmark, simple_timeline, tmp_path):
    """Benchmark full synthesis flow with mocked Kokoro."""
    config = KokoroConfig(output_dir=str(tmp_path))
    backend = KokoroBackend(config=config)
    backend._initialized = True
    backend._voice = "af_heart"

    mock_kokoro = MagicMock()
    fake_audio = np.zeros(24000, dtype=np.float32)
    mock_kokoro.create.return_value = (fake_audio, 24000)
    backend._kokoro = mock_kokoro

    def _run():
        backend.synthesize(simple_timeline)

    benchmark(_run)
