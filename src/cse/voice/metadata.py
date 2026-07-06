"""Voice Package Metadata (PRD-007 §6)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VoiceMetadata:
    """Immutable metadata for a Voice Package."""
    
    id: str
    name: str
    version: str
    author: str
    language: str
    backend: str
    sample_rate: int
    channels: int
    description: str
    license: str
