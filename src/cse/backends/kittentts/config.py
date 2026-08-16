"""KittenTTS Backend Configuration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class KittenTTSConfig:
    """Configuration for the KittenTTS backend."""

    model_name: str = "KittenML/kitten-tts-nano-0.8"
    cache_dir: Path | str | None = None
    default_voice: str = "expr-voice-2-f"
    default_speed: float = 1.0
    sample_rate: int = 24000
    output_dir: Path | str = "outputs/kittentts"
