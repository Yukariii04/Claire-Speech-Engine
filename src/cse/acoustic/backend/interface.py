"""Acoustic Backend Interface (PRD-005 §5-6)."""

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
