"""Acoustic Backend package."""

from __future__ import annotations

from cse.acoustic.backend.capabilities import BackendCapabilities
from cse.acoustic.backend.dummy_backend import DummyBackend
from cse.acoustic.backend.exceptions import (
    BackendError,
    BackendNotFoundError,
    BackendRegistrationError,
    BackendValidationError,
)
from cse.acoustic.backend.interface import AcousticBackend
from cse.acoustic.backend.manager import BackendManager
from cse.acoustic.backend.registry import BackendRegistry

__all__ = [
    "AcousticBackend",
    "BackendCapabilities",
    "BackendError",
    "BackendManager",
    "BackendNotFoundError",
    "BackendRegistrationError",
    "BackendRegistry",
    "BackendValidationError",
    "DummyBackend",
]
