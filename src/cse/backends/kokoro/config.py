"""Kokoro Backend Configuration (PRD-008 §7)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class KokoroConfig:
    """Configuration for the Kokoro backend."""

    lang_code: str = "en-us"
    sample_rate: int = 24000
    default_voice: str = "af_heart"
    output_dir: str = "temp"
    model_path: Path = Path("kokoro-v1.0.onnx")
    voices_path: Path = Path("voices-v1.0.bin")
