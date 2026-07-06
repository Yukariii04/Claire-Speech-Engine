"""Benchmarks for Voice Package System (PRD-007 §13)."""

from __future__ import annotations

import pytest
import yaml

from cse.voice import PackageLoader, PackageRegistry


@pytest.fixture
def mock_voice_dir(tmp_path):
    pkg_dir = tmp_path / "claire"
    pkg_dir.mkdir()
    meta_path = pkg_dir / "metadata.yaml"
    
    meta = {
        "id": "claire",
        "name": "Claire",
        "version": "1.0.0",
        "author": "CSE",
        "language": "en",
        "backend": "dummy",
        "sample_rate": 24000,
        "channels": 1,
        "description": "Test",
        "license": "MIT"
    }
    
    with open(meta_path, "w") as f:
        yaml.dump(meta, f)
        
    return str(pkg_dir)


def test_benchmark_package_discovery(benchmark, mock_voice_dir):
    """Benchmark package loading (discovery/metadata load combined)."""
    def _run():
        PackageLoader.load(mock_voice_dir)

    benchmark(_run)
    assert benchmark.stats["mean"] < 0.010, (
        f"Discovery mean {benchmark.stats['mean']:.4f}s exceeds 10ms target"
    )

def test_benchmark_registry_lookup(benchmark, mock_voice_dir):
    pkg = PackageLoader.load(mock_voice_dir)
    registry = PackageRegistry()
    registry.register(pkg)
    
    def _run():
        for _ in range(1000):
            registry.get("claire")

    benchmark(_run)
    assert benchmark.stats["mean"] < 0.010, (
        f"Lookup 1000x mean {benchmark.stats['mean']:.4f}s exceeds 10ms target"
    )
