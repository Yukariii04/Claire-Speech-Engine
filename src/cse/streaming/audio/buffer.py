"""Stream Buffer (PRD-006 §8)."""

from __future__ import annotations

import queue
from typing import Optional

from cse.streaming.audio.exceptions import BufferOverflowError
from cse.streaming.audio.frame import AudioFrame


class StreamBuffer:
    """Thread-safe FIFO queue for AudioFrames."""

    def __init__(self, maxsize: int = 0) -> None:
        self._queue: queue.Queue[AudioFrame] = queue.Queue(maxsize=maxsize)

    def push(self, frame: AudioFrame, timeout: float | None = None) -> None:
        """Push a frame into the buffer.
        
        Args:
            frame: The frame to push.
            timeout: Optional timeout for blocking push.
            
        Raises:
            BufferOverflowError: If the buffer is full.
        """
        try:
            self._queue.put(frame, block=timeout is not None, timeout=timeout)
        except queue.Full as e:
            raise BufferOverflowError("Stream buffer overflow") from e

    def pop(self, timeout: float | None = None) -> Optional[AudioFrame]:
        """Pop a frame from the buffer.
        
        Args:
            timeout: Optional timeout for blocking pop.
            
        Returns:
            The popped frame, or None if the buffer is empty and timeout expires.
        """
        try:
            return self._queue.get(block=timeout is not None, timeout=timeout)
        except queue.Empty:
            return None

    def flush(self) -> None:
        """Clear the buffer completely."""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except queue.Empty:
                break

    def size(self) -> int:
        """Return the approximate number of frames in the buffer."""
        return self._queue.qsize()
