"""Stream Validator (PRD-006 §10)."""

from __future__ import annotations

from cse.streaming.audio.exceptions import InvalidAudioFrameError, ClosedStreamError
from cse.streaming.audio.frame import AudioFrame


def validate_frame(frame: AudioFrame) -> None:
    """Validate an AudioFrame's integrity."""
    if frame.sample_rate <= 0:
        raise InvalidAudioFrameError(f"Invalid sample rate: {frame.sample_rate}")
    if frame.channels <= 0:
        raise InvalidAudioFrameError(f"Invalid channels: {frame.channels}")
    if frame.duration_ms <= 0:
        raise InvalidAudioFrameError(f"Duration must be positive: {frame.duration_ms}")
    if not isinstance(frame.samples, bytes):
        raise InvalidAudioFrameError("Samples must be bytes")
    if not frame.sample_format:
        raise InvalidAudioFrameError("Sample format cannot be empty")


def validate_stream_open(closed: bool) -> None:
    """Validate that the stream is open."""
    if closed:
        raise ClosedStreamError("Cannot operate on a closed stream.")
