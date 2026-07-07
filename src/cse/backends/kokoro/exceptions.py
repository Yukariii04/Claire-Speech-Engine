"""Kokoro Backend Exceptions (PRD-008 §10)."""

from __future__ import annotations


class KokoroBackendError(Exception):
    """Base exception for Kokoro backend errors."""


class KokoroInitializationError(KokoroBackendError):
    """Raised when Kokoro fails to initialize."""


class VoiceLoadError(KokoroBackendError):
    """Raised when a voice fails to load."""


class SpeechGenerationError(KokoroBackendError):
    """Raised when speech generation fails."""
