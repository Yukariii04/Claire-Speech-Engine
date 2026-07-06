"""Audio Frame (PRD-006 §6)."""

from __future__ import annotations

from dataclasses import dataclass
import uuid


@dataclass(frozen=True)
class AudioFrame:
    """Immutable chunk of PCM audio data."""
    
    uuid: uuid.UUID
    timestamp_ms: float
    sample_rate: int
    channels: int
    sample_format: str  # PCM-format agnostic (e.g. 'PCM_16', 'PCM_F32LE')
    samples: bytes
    duration_ms: float
