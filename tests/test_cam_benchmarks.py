"""Tests for CAM-001 Long-Utterance Benchmark Suite (PRD-028 §23, §24, §25)."""

import pytest

from cse.acoustic.cam.benchmark import BENCHMARK_PROMPTS, run_full_cam_benchmark


class TestCAMBenchmarks:
    def test_benchmark_prompts_defined_for_10_25_50_100_words(self):
        assert 10 in BENCHMARK_PROMPTS
        assert 25 in BENCHMARK_PROMPTS
        assert 50 in BENCHMARK_PROMPTS
        assert 100 in BENCHMARK_PROMPTS

        for word_target, text in BENCHMARK_PROMPTS.items():
            actual_count = len(text.split())
            # Assert approximately matched count
            assert abs(actual_count - word_target) <= 5

    def test_run_full_cam_benchmark_executes_successfully(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CSE_CAM_CACHE_DIR", str(tmp_path / "bench_cache"))
        res = run_full_cam_benchmark(quantized=True)
        assert res["status"] == "PASS"
        assert "CPU" in res["benchmarks"]

        cpu_res = res["benchmarks"]["CPU"]
        assert "10_words" in cpu_res
        assert "25_words" in cpu_res
        assert "50_words" in cpu_res
        assert "100_words" in cpu_res

        for length_key in ("10_words", "25_words", "50_words", "100_words"):
            item = cpu_res[length_key]
            assert item["acoustic_latency_ms"] > 0
            assert item["vocoder_latency_ms"] > 0
            assert item["total_latency_ms"] > 0
            assert item["sample_rate"] == 24000
            assert item["output_stability"] == "STABLE"
