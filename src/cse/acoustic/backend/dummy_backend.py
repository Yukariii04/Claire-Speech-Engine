"""Dummy Backend (PRD-005 §10)."""

from __future__ import annotations
from typing import Any

from cse.acoustic.backend.capabilities import BackendCapabilities
from cse.acoustic.backend.interface import AcousticBackend


class DummyBackend(AcousticBackend):
    """A dummy backend that does not synthesize."""

    def initialize(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def synthesize(self, timeline: Any) -> Any:
        raise NotImplementedError("Dummy backend does not synthesize")

    def get_capabilities(self) -> BackendCapabilities:
        return BackendCapabilities(
            backend_name="dummy",
            supports_streaming=False,
            supports_batch=False,
            supports_multispeaker=False,
            supports_voice_cloning=False,
            emotion="none",
            sample_rate=24000,
            requires_gpu=False,
            supported_languages=("en",),
            backend_version="1.0.0",
        )

    def validate_timeline(self, timeline: Any) -> None:
        pass
