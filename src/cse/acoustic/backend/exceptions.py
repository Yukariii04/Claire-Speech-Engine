"""Acoustic Backend Exceptions (PRD-005 §12)."""

from __future__ import annotations


class BackendError(Exception):
    """Base exception for acoustic backend errors."""


class BackendRegistrationError(BackendError):
    """Raised when registering or unregistering a backend fails."""


class BackendValidationError(BackendError):
    """Raised when timeline validation fails before synthesis."""


class BackendNotFoundError(BackendError):
    """Raised when a requested backend cannot be found."""
