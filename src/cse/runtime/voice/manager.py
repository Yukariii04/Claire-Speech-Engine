"""Voice Manager (PRD-004 §7-8)."""

from __future__ import annotations

import yaml
from pathlib import Path

from cse.runtime.voice.exceptions import VoiceNotFoundError


class VoiceManager:
    """Manages discovery and loading of voice metadata."""

    def __init__(self, voices_dir: str = "voices") -> None:
        self.voices_dir = Path(voices_dir)
        self._loaded_metadata: dict[str, str] | None = None

    def load_voice(self, voice_id: str) -> None:
        """Load metadata for a voice by ID."""
        voice_path = self.voices_dir / voice_id / "metadata.yaml"
        
        if not voice_path.exists():
            # Support fallback for testing
            raise VoiceNotFoundError(f"Voice {voice_id} not found at {voice_path}")

        try:
            with open(voice_path, "r", encoding="utf-8") as f:
                self._loaded_metadata = yaml.safe_load(f)
        except Exception as e:
            raise VoiceNotFoundError(f"Failed to load {voice_id}: {e}") from e

    def unload_voice(self) -> None:
        """Unload the currently loaded voice."""
        self._loaded_metadata = None

    def get_loaded_voice(self) -> dict[str, str] | None:
        """Get the currently loaded voice metadata."""
        return self._loaded_metadata
