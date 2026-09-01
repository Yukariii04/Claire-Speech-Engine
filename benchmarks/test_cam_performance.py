"""Performance and Latency Benchmark for CAM-001 Native Acoustic Pipeline."""

import pytest
from cse.acoustic.cam.benchmark import run_full_cam_benchmark


def test_cam_long_utterance_performance(benchmark):
    """Benchmark full CAM pipeline long-utterance synthesis execution."""
    res = benchmark(run_full_cam_benchmark, quantized=True)
    assert res["status"] == "PASS"
    assert "CPU" in res["benchmarks"]
