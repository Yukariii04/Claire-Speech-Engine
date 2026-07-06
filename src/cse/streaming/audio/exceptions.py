"""Audio Streaming Exceptions (PRD-006 §11)."""

from __future__ import annotations


class AudioStreamError(Exception):
    """Base exception for audio streaming errors."""


class BufferOverflowError(AudioStreamError):
    """Raised when the stream buffer overflows."""


class InvalidAudioFrameError(AudioStreamError):
    """Raised when an audio frame is invalid."""


class ClosedStreamError(AudioStreamError):
    """Raised when operating on a closed stream."""
