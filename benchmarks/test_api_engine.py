"""Benchmarks for the Public API SpeechEngine (PRD-009, PRD-012)."""

import pytest
from cse import SpeechEngine

def test_engine_creation_overhead(benchmark):
    """Engine creation must be <100ms."""
    def create_engine():
        engine = SpeechEngine()
        engine.shutdown()

    # The benchmark should run fast since initialization is minimal
    benchmark(create_engine)
    assert benchmark.stats["mean"] < 0.100, (
        f"Engine creation mean {benchmark.stats['mean']:.3f}s exceeds 100ms target"
    )


from unittest.mock import patch

def test_speech_request_overhead(benchmark):
    """Speech request overhead must be <10ms, excluding backend synthesis.
    
    We mock `_runtime.process` to exclude the actual synthesis and just
    measure the API routing, CIR building, and compiler overhead.
    """
    engine = SpeechEngine()
    engine._voice_loaded = True 
    
    with patch.object(engine._runtime, 'process', return_value=None):
        def speak():
            engine.speak("This is a test of the API overhead.")

        benchmark(speak)
    assert benchmark.stats["mean"] < 0.010, (
        f"Speech overhead mean {benchmark.stats['mean']:.4f}s exceeds 10ms target"
    )
    engine.shutdown()
