"""CAM-001 ONNX Export and INT8 Quantization Engine (PRD-028 §3, §5, §18, §19, §20, §22).

Exports:
- `cam_acoustic.onnx` with verified dynamic axes for phoneme length and frame length.
- `cam_vocoder.onnx` with verified dynamic axes for frame length and audio samples.
- Dynamic INT8 quantization for both graphs.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Tuple

import numpy as np
import onnx
import onnxruntime as ort
import torch
from loguru import logger

from cse.acoustic.cam.acoustic_model import CamAcousticModel
from cse.acoustic.cam.config import CAMConfig
from cse.acoustic.cam.vocoder import CamVocoder


class AcousticExportWrapper(torch.nn.Module):
    """Wrapper to cleanly expose continuous/discrete inputs for ONNX export."""

    def __init__(self, model: CamAcousticModel) -> None:
        super().__init__()
        self.model = model

    def forward(
        self,
        phoneme_ids: torch.Tensor,       # [B, T_phone] int64
        speaker_id: torch.Tensor,        # [B] int64
        style_id: torch.Tensor,          # [B] int64
        intent_id: torch.Tensor,         # [B] int64
        pace: torch.Tensor,              # [B] float32
        pitch_contour_id: torch.Tensor,  # [B] int64
        emphasis_id: torch.Tensor,       # [B] int64
    ) -> tuple[torch.Tensor, torch.Tensor]:
        mel, dur = self.model(
            phoneme_ids=phoneme_ids,
            speaker_id=speaker_id,
            style_id=style_id,
            intent_id=intent_id,
            pace=pace,
            pitch_contour_id=pitch_contour_id,
            emphasis_id=emphasis_id,
        )
        return mel, dur


def export_cam_acoustic_onnx(
    model: CamAcousticModel,
    output_path: str | Path,
    opset_version: int = 18,
) -> Path:
    """Export the CAM Acoustic Model to ONNX with dynamic sequence lengths (PRD-028 §18).

    Args:
        model: CamAcousticModel instance.
        output_path: Filepath where the .onnx model should be saved.
        opset_version: ONNX operator set version (default: 18).

    Returns:
        Path to exported ONNX model.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    wrapper = AcousticExportWrapper(model).eval()
    dev = next(model.parameters()).device

    # Dummy inputs for graph tracing
    dummy_phoneme_ids = torch.tensor([[2, 10, 20, 30, 40, 3]], dtype=torch.long, device=dev)  # [1, 6]
    dummy_speaker_id = torch.tensor([0], dtype=torch.long, device=dev)
    dummy_style_id = torch.tensor([0], dtype=torch.long, device=dev)
    dummy_intent_id = torch.tensor([0], dtype=torch.long, device=dev)
    dummy_pace = torch.tensor([1.0], dtype=torch.float32, device=dev)
    dummy_pitch_contour_id = torch.tensor([0], dtype=torch.long, device=dev)
    dummy_emphasis_id = torch.tensor([0], dtype=torch.long, device=dev)

    input_names = [
        "phoneme_ids",
        "speaker_id",
        "style_id",
        "intent_id",
        "pace",
        "pitch_contour_id",
        "emphasis_id",
    ]
    output_names = ["mel_output", "durations"]

    dynamic_axes = {
        "phoneme_ids": {0: "batch", 1: "phone_len"},
        "speaker_id": {0: "batch"},
        "style_id": {0: "batch"},
        "intent_id": {0: "batch"},
        "pace": {0: "batch"},
        "pitch_contour_id": {0: "batch"},
        "emphasis_id": {0: "batch"},
        "mel_output": {0: "batch", 1: "frame_len"},
        "durations": {0: "batch", 1: "phone_len"},
    }

    logger.info(f"Exporting cam_acoustic to ONNX -> {output_path}")

    # Set UTF-8 encoding environment variable to prevent Windows cp1252 export logging issues
    os.environ["PYTHONIOENCODING"] = "utf-8"

    torch.onnx.export(
        wrapper,
        (
            dummy_phoneme_ids,
            dummy_speaker_id,
            dummy_style_id,
            dummy_intent_id,
            dummy_pace,
            dummy_pitch_contour_id,
            dummy_emphasis_id,
        ),
        str(output_path),
        input_names=input_names,
        output_names=output_names,
        dynamic_axes=dynamic_axes,
        opset_version=opset_version,
        dynamo=False,
    )

    # Validate exported model structure
    onnx_model = onnx.load(str(output_path))
    onnx.checker.check_model(onnx_model)
    logger.info(f"Successfully exported and validated {output_path}")
    return output_path


def export_cam_vocoder_onnx(
    vocoder: CamVocoder,
    output_path: str | Path,
    opset_version: int = 18,
) -> Path:
    """Export the CAM Vocoder to ONNX with dynamic frame length (PRD-028 §18, §20).

    Args:
        vocoder: CamVocoder instance.
        output_path: Filepath where the .onnx model should be saved.
        opset_version: ONNX operator set version (default: 18).

    Returns:
        Path to exported ONNX model.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    vocoder = vocoder.eval()

    # Dummy mel input [1, 50, n_mels]
    dev = next(vocoder.parameters()).device
    n_mels = getattr(vocoder, "n_mels", 100)
    dummy_mel = torch.randn(1, 50, n_mels, dtype=torch.float32, device=dev)

    input_names = ["mel"]
    output_names = ["waveform"]

    dynamic_axes = {
        "mel": {0: "batch", 1: "frame_len"},
        "waveform": {0: "batch", 2: "audio_len"},
    }

    logger.info(f"Exporting cam_vocoder to ONNX -> {output_path}")

    os.environ["PYTHONIOENCODING"] = "utf-8"

    torch.onnx.export(
        vocoder,
        (dummy_mel,),
        str(output_path),
        input_names=input_names,
        output_names=output_names,
        dynamic_axes=dynamic_axes,
        opset_version=opset_version,
        dynamo=False,
    )

    onnx_model = onnx.load(str(output_path))
    onnx.checker.check_model(onnx_model)
    logger.info(f"Successfully exported and validated {output_path}")
    return output_path


def quantize_cam_onnx(
    input_model_path: str | Path,
    output_model_path: str | Path,
) -> Path:
    """Quantize an ONNX model to INT8 (PRD-028 §3, §22).

    Args:
        input_model_path: Source FP32 ONNX model path.
        output_model_path: Target INT8 ONNX model path.

    Returns:
        Path to quantized model.
    """
    from onnxruntime.quantization import quantize_dynamic, QuantType

    input_path = Path(input_model_path)
    output_path = Path(output_model_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    logger.info(f"Quantizing ONNX model {input_path} -> {output_path}")
    quantize_dynamic(
        model_input=str(input_path),
        model_output=str(output_path),
        weight_type=QuantType.QInt8,
    )
    logger.info(f"Quantization complete: {output_path}")
    return output_path


def get_model_size_mb(path: str | Path) -> float:
    """Return model file size in Megabytes (MB)."""
    return Path(path).stat().st_size / (1024.0 * 1024.0)


def validate_onnx_inference(
    acoustic_path: str | Path,
    vocoder_path: str | Path,
    phone_lens: tuple[int, ...] = (10, 25, 50, 100),
    providers: Sequence[str] = ("CPUExecutionProvider",),
) -> dict[str, Any]:
    """Validate dynamic length variable inference across both ONNX stages (PRD-028 §18, §23).

    Returns a structured verification report.
    """
    session_opt = ort.SessionOptions()
    session_opt.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

    acoustic_session = ort.InferenceSession(str(acoustic_path), session_opt, providers=list(providers))
    vocoder_session = ort.InferenceSession(str(vocoder_path), session_opt, providers=list(providers))

    results = []

    for length in phone_lens:
        dummy_ids = np.random.randint(1, 100, size=(1, length), dtype=np.int64)
        dummy_ids[0, 0] = 2   # BOS
        dummy_ids[0, -1] = 3  # EOS

        feed_acoustic = {
            "phoneme_ids": dummy_ids,
            "speaker_id": np.array([0], dtype=np.int64),
            "style_id": np.array([0], dtype=np.int64),
            "intent_id": np.array([0], dtype=np.int64),
            "pace": np.array([1.0], dtype=np.float32),
            "pitch_contour_id": np.array([0], dtype=np.int64),
            "emphasis_id": np.array([0], dtype=np.int64),
        }

        # 1. Acoustic inference
        acoustic_out = acoustic_session.run(None, feed_acoustic)
        mel_output, durations = acoustic_out[0], acoustic_out[1]

        assert mel_output.shape[0] == 1
        assert mel_output.shape[2] == 100, f"Expected 100-channel mel-spectrogram, got {mel_output.shape[2]}"
        assert mel_output.shape[1] == int(durations.sum())

        # 2. Vocoder inference
        vocoder_out = vocoder_session.run(None, {"mel": mel_output})
        waveform = vocoder_out[0]

        expected_samples = mel_output.shape[1] * 256
        assert waveform.shape[0] == 1
        assert waveform.shape[1] == 1
        assert waveform.shape[2] == expected_samples

        results.append({
            "phone_len": length,
            "frame_len": mel_output.shape[1],
            "audio_samples": waveform.shape[2],
            "duration_sec": waveform.shape[2] / 24000.0,
        })

    return {
        "status": "PASS",
        "acoustic_inputs": [i.name for i in acoustic_session.get_inputs()],
        "acoustic_outputs": [o.name for o in acoustic_session.get_outputs()],
        "vocoder_inputs": [i.name for i in vocoder_session.get_inputs()],
        "vocoder_outputs": [o.name for o in vocoder_session.get_outputs()],
        "length_tests": results,
    }
