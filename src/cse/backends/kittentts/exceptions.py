"""KittenTTS Backend Exceptions."""

from __future__ import annotations


class KittenTTSBackendError(Exception):
    """Base exception for all KittenTTS backend errors."""
    pass


class KittenTTSInitializationError(KittenTTSBackendError):
    """Raised when KittenTTS backend fails to initialize."""
    pass


class VoiceLoadError(KittenTTSBackendError):
    """Raised when a voice fails to load or is invalid."""
    pass


class SpeechGenerationError(KittenTTSBackendError):
    """Raised when speech synthesis fails."""
    pass
