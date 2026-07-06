"""CIR-specific exception hierarchy."""

from __future__ import annotations


class CIRBuilderError(Exception):
    """Raised when the CIR builder cannot construct a document."""


class CIRValidationError(Exception):
    """Raised when a CIRDocument fails validation."""


class CIRSerializationError(Exception):
    """Raised on serialization / deserialization failures."""
