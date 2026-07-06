"""Audio Stream (PRD-006 §7)."""

from __future__ import annotations

import uuid
from typing import Any

from cse.streaming.audio.frame import AudioFrame
from cse.streaming.audio.validator import validate_stream_open, validate_frame


class AudioStream:
    """Contains ordered AudioFrames."""

    def __init__(self, stream_uuid: uuid.UUID | None = None, metadata: dict[str, Any] | None = None) -> None:
        self.uuid = stream_uuid or uuid.uuid4()
        self.metadata = metadata or {}
        self.frames: list[AudioFrame] = []
        self.closed = False

    def append(self, frame: AudioFrame) -> None:
        """Append an audio frame to the stream."""
        validate_stream_open(self.closed)
        validate_frame(frame)
        self.frames.append(frame)

    def close(self) -> None:
        """Close the stream."""
        self.closed = True

    def frame_count(self) -> int:
        """Return the total number of frames in the stream."""
        return len(self.frames)

    def duration(self) -> float:
        """Return the total duration of the stream in milliseconds."""
        return sum(f.duration_ms for f in self.frames)
