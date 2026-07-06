"""Performance compiler exception hierarchy."""

from __future__ import annotations


class PerformanceCompilerError(Exception):
    """Raised when the performance compiler cannot construct a timeline."""


class TimelineValidationError(Exception):
    """Raised when a PerformanceTimeline fails validation."""


class TimelineSerializationError(Exception):
    """Raised on serialization / deserialization failures."""
