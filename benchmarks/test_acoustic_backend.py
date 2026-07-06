"""Benchmarks for Acoustic Backend (PRD-005 §15)."""

from __future__ import annotations

import pytest

from cse.acoustic.backend import BackendManager, BackendRegistry, DummyBackend


def test_benchmark_backend_lookup(benchmark):
    """Benchmark 1000 backend lookups."""
    registry = BackendRegistry()
    registry.register_backend("dummy", DummyBackend())
    
    def _run():
        for _ in range(1000):
            registry.get_backend("dummy")

    benchmark(_run)
    assert benchmark.stats["mean"] < 0.010, (
        f"Lookup 1000x mean {benchmark.stats['mean']:.4f}s exceeds 10ms target"
    )

def test_benchmark_backend_manager_init(benchmark):
    registry = BackendRegistry()
    dummy = DummyBackend()
    registry.register_backend("dummy", dummy)
    
    manager = BackendManager(registry)
    manager.select("dummy")
    
    def _run():
        manager.initialize()
        manager.shutdown()
        
    benchmark(_run)
