"""Tests for CAM-001 ONNX Export, Dynamic Lengths, Quantization, and Runtime (PRD-028 §3, §5, §18, §19, §20, §22)."""

import os
from pathlib import Path
import pytest
import numpy as np
import onnxruntime as ort

from cse.acoustic.cam.acoustic_model import CamAcousticModel
from cse.acoustic.cam.config import CAMConfig
from cse.acoustic.cam.onnx_export import (
    export_cam_acoustic_onnx,
    export_cam_vocoder_onnx,
    get_model_size_mb,
    quantize_cam_onnx,
    validate_onnx_inference,
)
from cse.acoustic.cam.vocoder import CamVocoder


@pytest.fixture(scope="module")
def export_dir(tmp_path_factory):
    d = tmp_path_factory.mktemp("cam_onnx_test")
    return d


@pytest.fixture(scope="module")
def exported_models(export_dir):
    ac_model = CamAcousticModel().eval()
    voc_model = CamVocoder().eval()

    ac_path = export_dir / "cam_acoustic.onnx"
    voc_path = export_dir / "cam_vocoder.onnx"

    export_cam_acoustic_onnx(ac_model, ac_path)
    export_cam_vocoder_onnx(voc_model, voc_path)

    # Quantize
    quant_ac_path = export_dir / "cam_acoustic_int8.onnx"
    quant_voc_path = export_dir / "cam_vocoder_int8.onnx"

    quantize_cam_onnx(ac_path, quant_ac_path)
    quantize_cam_onnx(voc_path, quant_voc_path)

    return {
        "acoustic": ac_path,
        "vocoder": voc_path,
        "quant_acoustic": quant_ac_path,
        "quant_vocoder": quant_voc_path,
    }


class TestCAMONNXExport:
    def test_both_onnx_files_created(self, exported_models):
        assert exported_models["acoustic"].exists()
        assert exported_models["vocoder"].exists()
        assert exported_models["quant_acoustic"].exists()
        assert exported_models["quant_vocoder"].exists()

    def test_model_size_under_100mb(self, exported_models):
        fp32_ac_size = get_model_size_mb(exported_models["acoustic"])
        fp32_voc_size = get_model_size_mb(exported_models["vocoder"])
        quant_ac_size = get_model_size_mb(exported_models["quant_acoustic"])
        quant_voc_size = get_model_size_mb(exported_models["quant_vocoder"])

        total_quant_size = quant_ac_size + quant_voc_size
        print(f"\nFP32 Size: Acoustic={fp32_ac_size:.2f}MB, Vocoder={fp32_voc_size:.2f}MB, Total={fp32_ac_size + fp32_voc_size:.2f}MB")
        print(f"INT8 Size: Acoustic={quant_ac_size:.2f}MB, Vocoder={quant_voc_size:.2f}MB, Total={total_quant_size:.2f}MB")

        # Must satisfy <= ~100MB (PRD-028 §3)
        assert total_quant_size <= 100.0

    def test_dynamic_length_inference_fp32(self, exported_models):
        res = validate_onnx_inference(
            acoustic_path=exported_models["acoustic"],
            vocoder_path=exported_models["vocoder"],
            phone_lens=(10, 25, 50, 100),
        )
        assert res["status"] == "PASS"
        assert len(res["length_tests"]) == 4

    def test_dynamic_length_inference_quantized(self, exported_models):
        res = validate_onnx_inference(
            acoustic_path=exported_models["quant_acoustic"],
            vocoder_path=exported_models["quant_vocoder"],
            phone_lens=(10, 25, 50, 100),
        )
        assert res["status"] == "PASS"
        assert len(res["length_tests"]) == 4

    def test_variable_vocoder_input_lengths(self, exported_models):
        voc_sess = ort.InferenceSession(str(exported_models["vocoder"]), providers=["CPUExecutionProvider"])
        for num_frames in (12, 45, 128, 300):
            dummy_mel = np.random.randn(1, num_frames, 80).astype(np.float32)
            out = voc_sess.run(None, {"mel": dummy_mel})[0]
            assert out.shape == (1, 1, num_frames * 256)
