"""Backend Capabilities (PRD-005 §7)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BackendCapabilities:
    """Immutable capabilities of an acoustic backend.

    ``supports_batch`` indicates whether the public ``translate()`` API
    accepts batched input (multiple ``PerformanceGraph`` instances per
    call).  It does **not** describe whether the underlying model uses
    dynamic ONNX batch axes internally.
    """
    
    backend_name: str
    supports_streaming: bool
    supports_batch: bool
    supports_multispeaker: bool
    supports_voice_cloning: bool
    emotion: str
    sample_rate: int
    requires_gpu: bool
    supported_languages: tuple[str, ...]
    backend_version: str
