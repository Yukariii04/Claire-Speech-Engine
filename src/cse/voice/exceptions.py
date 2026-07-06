"""Voice Package Exceptions (PRD-007 §10)."""

from __future__ import annotations


class VoicePackageError(Exception):
    """Base exception for voice package errors."""


class InvalidVoicePackageError(VoicePackageError):
    """Raised when a voice package fails validation."""


class VoicePackageNotFoundError(VoicePackageError):
    """Raised when a requested voice package cannot be found."""
