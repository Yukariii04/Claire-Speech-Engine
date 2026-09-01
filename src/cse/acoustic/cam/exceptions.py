"""CAM Backend Exceptions."""

from __future__ import annotations

from cse.acoustic.backend.exceptions import BackendError


class CAMBackendError(BackendError):
    """Base exception for all CAM backend errors."""
    pass


class CAMInitializationError(CAMBackendError):
    """Raised when CAM backend fails to initialize."""
    pass


class VoiceLoadError(CAMBackendError):
    """Raised when a CAM voice fails to load or is invalid."""
    pass


class SpeechGenerationError(CAMBackendError):
    """Raised when CAM speech synthesis fails."""
    pass
