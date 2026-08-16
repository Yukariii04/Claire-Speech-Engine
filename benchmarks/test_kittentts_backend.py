"""Benchmarks for KittenTTS Backend (PRD-012)."""

from __future__ import annotations

from unittest.mock import MagicMock

import numpy as np
import pytest

from cse.backends.kittentts.backend import KittenTTSBackend
from cse.backends.kittentts.config import KittenTTSConfig
from cse.performance.graph import PerformanceGraph


@pytest.fixture
def simple_graph():
    return PerformanceGraph(
        text="Hello world, this is a test sentence.",
        character_state=None,
        semantics={},
        intent={},
        plan={"delivery": {"pace": "moderate"}},
    )


def test_benchmark_kittentts_synthesis(benchmark, simple_graph, tmp_path):
    """Benchmark KittenTTS single sentence synthesis."""
    config = KittenTTSConfig(output_dir=str(tmp_path))
    backend = KittenTTSBackend(config=config)
    backend.initialize()
    backend.load_voice("expr-voice-2-f")

    def _run():
        backend.translate(simple_graph)

    benchmark(_run)
    backend.shutdown()


def test_benchmark_mocked_synthesis(benchmark, simple_graph, tmp_path):
    """Benchmark full synthesis flow with mocked KittenTTS."""
    config = KittenTTSConfig(output_dir=str(tmp_path))
    backend = KittenTTSBackend(config=config)
    backend.initialize()
    backend.load_voice("expr-voice-2-f")

    mock_model = MagicMock()
    fake_audio = np.zeros(24000, dtype=np.float32)
    mock_model.generate.return_value = fake_audio
    backend._ensure_model = MagicMock()
    backend._model = mock_model

    def _run():
        backend.translate(simple_graph)

    benchmark(_run)
