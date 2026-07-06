"""Acoustic Backend Interface (PRD-004 §9-10)."""

from __future__ import annotations

from abc import ABC, abstractmethod


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
    def synthesize(self, timeline: object) -> object:
        """Synthesize a performance timeline into audio.
        
        Args:
            timeline: The PerformanceTimeline to synthesize.
            
        Returns:
            The synthesized audio output.
        """
        pass

    @abstractmethod
    def supports_streaming(self) -> bool:
        """Return whether the backend supports streaming."""
        pass


class DummyBackend(AcousticBackend):
    """A dummy backend that does not synthesize (PRD §10)."""

    def initialize(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def synthesize(self, timeline: object) -> object:
        # Expected behavior per PRD §10 and §18
        raise NotImplementedError("Dummy backend does not synthesize")

    def supports_streaming(self) -> bool:
        return False
