"""Public API Exceptions (PRD-009 §10)."""

from __future__ import annotations


class SpeechEngineError(Exception):
    """Base exception for all public API errors."""


class VoiceNotLoadedError(SpeechEngineError):
    """Raised when attempting to speak before loading a voice."""


class ConfigurationError(SpeechEngineError):
    """Raised when the engine receives an invalid configuration."""
