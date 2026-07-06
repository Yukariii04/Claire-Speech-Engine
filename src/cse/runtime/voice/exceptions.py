"""Voice Runtime Exceptions (PRD-004 §13)."""

from __future__ import annotations


class VoiceRuntimeError(Exception):
    """Base exception for voice runtime errors."""


class VoiceNotFoundError(VoiceRuntimeError):
    """Raised when a requested voice package cannot be found."""


class BackendNotRegisteredError(VoiceRuntimeError):
    """Raised when trying to synthesize without an active backend."""


class InvalidRuntimeStateError(VoiceRuntimeError):
    """Raised when an illegal state transition occurs."""
