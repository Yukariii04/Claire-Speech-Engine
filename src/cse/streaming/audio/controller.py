"""Stream Controller (PRD-006 §9)."""

from __future__ import annotations

from typing import Optional

from cse.streaming.audio.buffer import StreamBuffer
from cse.streaming.audio.frame import AudioFrame
from cse.streaming.audio.stream import AudioStream
from cse.streaming.audio.validator import validate_stream_open


class StreamController:
    """Manages stream lifecycle and coordinates the buffer."""

    def __init__(self, max_buffer_size: int = 1000) -> None:
        self.stream: AudioStream | None = None
        self.buffer = StreamBuffer(maxsize=max_buffer_size)

    def create_stream(self) -> AudioStream:
        """Create and own a new AudioStream."""
        self.stream = AudioStream()
        self.buffer.flush()
        return self.stream

    def push_frame(self, frame: AudioFrame, block_timeout: float | None = None) -> None:
        """Push a frame into the stream and buffer."""
        if not self.stream:
            raise ValueError("No active stream. Call create_stream() first.")
        
        validate_stream_open(self.stream.closed)
        self.stream.append(frame)
        self.buffer.push(frame, timeout=block_timeout)

    def pop_frame(self, block_timeout: float | None = None) -> Optional[AudioFrame]:
        """Pop a frame from the buffer."""
        return self.buffer.pop(timeout=block_timeout)

    def clear(self) -> None:
        """Clear the active buffer."""
        self.buffer.flush()

    def close(self) -> None:
        """Close the active stream."""
        if self.stream:
            self.stream.close()
