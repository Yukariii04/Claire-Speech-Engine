"""Voice Package (PRD-007)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from cse.voice.metadata import VoiceMetadata


@dataclass(frozen=True)
class VoicePackage:
    """Represents a fully loaded Voice Package."""
    
    metadata: VoiceMetadata
    path: Path
