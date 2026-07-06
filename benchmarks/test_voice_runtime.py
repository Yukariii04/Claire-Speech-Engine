"""Benchmarks for Voice Runtime (PRD-004 §16)."""

from __future__ import annotations

import pytest
import yaml

from cse.runtime.voice.manager import VoiceManager
from cse.runtime.voice.runtime import VoiceRuntime


@pytest.fixture
def mock_voice_dir(tmp_path):
    voice_dir = tmp_path / "claire"
    voice_dir.mkdir(parents=True)
    meta_file = voice_dir / "metadata.yaml"
    with open(meta_file, "w") as f:
        yaml.dump({"id": "claire", "name": "Claire"}, f)
    return str(tmp_path)


def test_benchmark_runtime_initialization(benchmark):
    """Runtime initialization should be < 20ms."""
    def _run():
        runtime = VoiceRuntime()
        runtime.initialize()

    benchmark(_run)
    assert benchmark.stats["mean"] < 0.020, (
        f"Initialization mean {benchmark.stats['mean']:.4f}s exceeds 20ms target"
    )


def test_benchmark_load_metadata(benchmark, mock_voice_dir):
    manager = VoiceManager(voices_dir=mock_voice_dir)
    runtime = VoiceRuntime(manager=manager)
    runtime.initialize()

    def _run():
        runtime.load_voice("claire")

    benchmark(_run)


def test_benchmark_unload_metadata(benchmark, mock_voice_dir):
    manager = VoiceManager(voices_dir=mock_voice_dir)
    runtime = VoiceRuntime(manager=manager)
    runtime.initialize()
    runtime.load_voice("claire")

    def _run():
        runtime.unload_voice()
        runtime._state = 2 # hack state to VOICE_LOADED to allow repeated unloading
        # wait, a better way is to just use manager directly or reload it.
        
    def _run_clean():
        runtime.load_voice("claire")
        runtime.unload_voice()

    benchmark(_run_clean)
