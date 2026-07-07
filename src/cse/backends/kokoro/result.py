"""SpeechResult (PRD-008 §6)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SpeechResult:
    """Immutable result of a speech synthesis operation."""

    success: bool
    audio_path: Path
    duration_seconds: float
    sample_rate: int
    channels: int
    backend: str
    voice: str
    metadata: dict[str, Any] = field(default_factory=dict)
