"""Backend Validation (PRD-005 §11)."""

from __future__ import annotations
from typing import Any

from cse.acoustic.backend.exceptions import BackendValidationError


def validate_backend_state(backend_initialized: bool, backend_active: bool) -> None:
    """Validate backend state before synthesis."""
    if not backend_active:
        raise BackendValidationError("No backend is currently active.")
    if not backend_initialized:
        raise BackendValidationError("Backend is not initialized.")
