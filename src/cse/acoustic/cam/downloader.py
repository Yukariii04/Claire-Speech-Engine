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
    """Resolve acoustic and vocoder ONNX model paths from local overrides, cache, or official distribution.

    Args:
        acoustic_path: Optional explicit acoustic ONNX file path.
        vocoder_path: Optional explicit vocoder ONNX file path.
        quantized: Whether to prefer INT8 quantized models.

    Returns:
        tuple[Path, Path]: (resolved_acoustic_path, resolved_vocoder_path).

    Raises:
        FileNotFoundError: If trained model files are not available. Silent random-weight
            fabrication is strictly prohibited.
    """
    cache_dir = get_cam_cache_dir()

    acoustic_name = "cam_acoustic_int8.onnx" if quantized else "cam_acoustic.onnx"
    vocoder_name = "cam_vocoder_int8.onnx" if quantized else "cam_vocoder.onnx"

    target_acoustic = Path(acoustic_path) if acoustic_path else cache_dir / acoustic_name
    target_vocoder = Path(vocoder_path) if vocoder_path else cache_dir / vocoder_name

    # 1. If explicit paths were provided but do not exist, fail immediately
    if acoustic_path and not target_acoustic.is_file():
        raise FileNotFoundError(f"Explicit CAM acoustic model file not found: {target_acoustic}")
    if vocoder_path and not target_vocoder.is_file():
        raise FileNotFoundError(f"Explicit CAM vocoder model file not found: {target_vocoder}")

    # 2. Check if cached models exist locally
    if target_acoustic.is_file() and target_vocoder.is_file():
        return target_acoustic, target_vocoder

    # 3. Attempt lazy download from remote release repository if not cached
    missing_models = []
    if not target_acoustic.is_file():
        missing_models.append((acoustic_name, target_acoustic))
    if not target_vocoder.is_file():
        missing_models.append((vocoder_name, target_vocoder))

    try:
        from huggingface_hub import hf_hub_download

        for filename, dest_path in missing_models:
            logger.info(f"Downloading CAM model {filename} from {CAM_DEFAULT_REPO_ID} to {dest_path}...")
            downloaded = hf_hub_download(
                repo_id=CAM_DEFAULT_REPO_ID,
                filename=filename,
                local_dir=str(cache_dir),
                revision=CAM_VERSION_PIN,
            )
            dest_path = Path(downloaded)
    except Exception as e:
        logger.debug(f"Remote CAM model download attempt failed for repository '{CAM_DEFAULT_REPO_ID}': {e}")

    # 4. Strictly verify availability — DO NOT fabricate random weights
    if not target_acoustic.is_file() or not target_vocoder.is_file():
        raise FileNotFoundError(
            f"Trained CAM model artifacts not found in local cache ('{cache_dir}') or remote repository ('{CAM_DEFAULT_REPO_ID}').\n"
            f"  - Acoustic Model: {target_acoustic} (exists: {target_acoustic.is_file()})\n"
            f"  - Vocoder Model:  {target_vocoder} (exists: {target_vocoder.is_file()})\n"
            "Trained weights must be produced via 'scripts/colab_train_cam_phase1.py' or downloaded from an official release.\n"
            "Silent fabrication of randomly initialized weights is strictly prohibited."
        )

    return target_acoustic, target_vocoder
