"""Public API Configuration (PRD-009 §8)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class EngineConfig:
    """Immutable configuration for the SpeechEngine."""
    
    config_path: Path | str | None = None
    overrides: dict[str, Any] = field(default_factory=dict)
