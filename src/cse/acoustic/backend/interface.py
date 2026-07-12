"""Acoustic Backend Interface (PRD-005 §5-6, PRD-015 §3)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from cse.acoustic.backend.capabilities import BackendCapabilities


class AcousticBackend(ABC):
    """Abstract interface for all acoustic synthesis backends."""

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the backend."""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """Shutdown the backend."""
        pass

    @abstractmethod
    def synthesize(self, timeline: Any) -> Any:
        """Synthesize a performance timeline into audio."""
        pass

    @abstractmethod
    def get_capabilities(self) -> BackendCapabilities:
        """Return the capabilities of this backend."""
        pass

    @abstractmethod
    def validate_timeline(self, timeline: Any) -> None:
        """Validate a timeline for this specific backend."""
        pass

    def list_voices(self) -> list[dict[str, str]]:
        """Return structured metadata for all voices this backend supports.

        Each dict should contain at minimum: 'id', 'name'.
        Optional keys: 'language', 'gender'.

        Backends that don't override this return an empty list.
        """
        return []

    def validate_voice(self, voice_id: str) -> bool:
        """Check whether a voice ID is valid for this backend.

        Returns True if the voice is available, False otherwise.
        Backends that don't override this accept any voice.
        """
        voices = self.list_voices()
        if not voices:
            return True  # Backend doesn't enumerate voices; accept anything
        return any(v["id"] == voice_id for v in voices)

