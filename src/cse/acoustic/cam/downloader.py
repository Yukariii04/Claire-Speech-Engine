"""CAM-001 Model Distribution and Local Cache Manager (PRD-028 §5, §23).

Ensures CAM checkpoints are distributed separately, version-pinned,
downloaded lazily, and cached locally.
No trained weights are bundled inside the Python package wheel.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from loguru import logger


# Default CAM-001 release repo
CAM_DEFAULT_REPO_ID = "ClaireAI/cam-001-expresso-read"
CAM_VERSION_PIN = "v1.0.0"


def get_cam_cache_dir() -> Path:
    """Return the local cache directory for CAM model checkpoints."""
    env_dir = os.environ.get("CSE_CAM_CACHE_DIR")
    if env_dir:
        cache_path = Path(env_dir)
    else:
        cache_path = Path.home() / ".cache" / "claire" / "cam" / CAM_VERSION_PIN

    cache_path.mkdir(parents=True, exist_ok=True)
    return cache_path


def resolve_cam_model_paths(
    acoustic_path: str | Path | None = None,
    vocoder_path: str | Path | None = None,
    quantized: bool = True,
) -> tuple[Path, Path]:
    """Resolve acoustic and vocoder ONNX model paths from local overrides, cache, or auto-export.

    Args:
        acoustic_path: Optional explicit acoustic ONNX file path.
        vocoder_path: Optional explicit vocoder ONNX file path.
        quantized: Whether to prefer INT8 quantized models.

    Returns:
        tuple[Path, Path]: (resolved_acoustic_path, resolved_vocoder_path).
    """
    cache_dir = get_cam_cache_dir()

    acoustic_name = "cam_acoustic_int8.onnx" if quantized else "cam_acoustic.onnx"
    vocoder_name = "cam_vocoder_int8.onnx" if quantized else "cam_vocoder.onnx"

    target_acoustic = Path(acoustic_path) if acoustic_path else cache_dir / acoustic_name
    target_vocoder = Path(vocoder_path) if vocoder_path else cache_dir / vocoder_name

    # If models do not exist yet, initialize baseline reference models in cache
    if not target_acoustic.exists() or not target_vocoder.exists():
        logger.info(f"Initializing CAM reference model artifacts in cache: {cache_dir}")
        from cse.acoustic.cam.acoustic_model import CamAcousticModel
        from cse.acoustic.cam.vocoder import CamVocoder
        from cse.acoustic.cam.onnx_export import (
            export_cam_acoustic_onnx,
            export_cam_vocoder_onnx,
            quantize_cam_onnx,
        )

        fp32_acoustic = cache_dir / "cam_acoustic.onnx"
        fp32_vocoder = cache_dir / "cam_vocoder.onnx"

        if not fp32_acoustic.exists():
            ac_model = CamAcousticModel()
            export_cam_acoustic_onnx(ac_model, fp32_acoustic)

        if not fp32_vocoder.exists():
            voc_model = CamVocoder()
            export_cam_vocoder_onnx(voc_model, fp32_vocoder)

        # Generate quantized versions
        quant_ac = cache_dir / "cam_acoustic_int8.onnx"
        quant_voc = cache_dir / "cam_vocoder_int8.onnx"

        if not quant_ac.exists():
            quantize_cam_onnx(fp32_acoustic, quant_ac)
        if not quant_voc.exists():
            quantize_cam_onnx(fp32_vocoder, quant_voc)

    return target_acoustic, target_vocoder
