"""Tests for StreamBuffer."""

from __future__ import annotations

import uuid
import pytest

from cse.streaming.audio.buffer import StreamBuffer
from cse.streaming.audio.exceptions import BufferOverflowError
from cse.streaming.audio.frame import AudioFrame


@pytest.fixture
def valid_frame():
    return AudioFrame(
        uuid=uuid.uuid4(),
        timestamp_ms=0.0,
        sample_rate=24000,
        channels=1,
        sample_format="PCM_16",
        samples=b"\x00\x00",
        duration_ms=10.0
    )


class TestStreamBuffer:
    def test_push_and_pop(self, valid_frame):
        buf = StreamBuffer(maxsize=10)
        buf.push(valid_frame)
        assert buf.size() == 1
        
        popped = buf.pop()
        assert popped is valid_frame
        assert buf.size() == 0

    def test_pop_empty_non_blocking(self):
        buf = StreamBuffer()
        assert buf.pop(timeout=0.0) is None
        assert buf.pop() is None

    def test_buffer_overflow(self, valid_frame):
        buf = StreamBuffer(maxsize=1)
        buf.push(valid_frame)
        
        with pytest.raises(BufferOverflowError):
            buf.push(valid_frame, timeout=0.0)

    def test_flush(self, valid_frame):
        buf = StreamBuffer(maxsize=5)
        for _ in range(3):
            buf.push(valid_frame)
            
        assert buf.size() == 3
        buf.flush()
        assert buf.size() == 0
