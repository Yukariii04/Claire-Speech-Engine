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
        cache_dir = tmp_path / "bench_cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("CSE_CAM_CACHE_DIR", str(cache_dir))

        from cse.acoustic.cam.acoustic_model import CamAcousticModel
        from cse.acoustic.cam.config import CAMConfig
        from cse.acoustic.cam.onnx_export import (
            export_cam_acoustic_onnx,
            export_cam_vocoder_onnx,
            quantize_cam_onnx,
        )
        from cse.acoustic.cam.vocoder import CamVocoder

        tiny_cfg = CAMConfig(n_mels=100, d_model=32)
        ac_model = CamAcousticModel(tiny_cfg)
        voc_model = CamVocoder(n_mels=100)

        fp32_ac = cache_dir / "cam_acoustic.onnx"
        fp32_voc = cache_dir / "cam_vocoder.onnx"
        export_cam_acoustic_onnx(ac_model, fp32_ac)
        export_cam_vocoder_onnx(voc_model, fp32_voc)

        quant_ac = cache_dir / "cam_acoustic_int8.onnx"
        quant_voc = cache_dir / "cam_vocoder_int8.onnx"
        quantize_cam_onnx(fp32_ac, quant_ac)
        quantize_cam_onnx(fp32_voc, quant_voc)

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
