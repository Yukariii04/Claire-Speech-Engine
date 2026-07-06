"""Tests for StreamController."""

from __future__ import annotations

import uuid
import pytest

from cse.streaming.audio.controller import StreamController
from cse.streaming.audio.frame import AudioFrame
from cse.streaming.audio.exceptions import ClosedStreamError


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


class TestStreamController:
    def test_create_and_push(self, valid_frame):
        controller = StreamController()
        
        with pytest.raises(ValueError):
            controller.push_frame(valid_frame)
            
        stream = controller.create_stream()
        assert stream is not None
        
        controller.push_frame(valid_frame)
        assert controller.stream.frame_count() == 1
        assert controller.buffer.size() == 1
        
        popped = controller.pop_frame()
        assert popped is valid_frame
        
        controller.close()
        with pytest.raises(ClosedStreamError):
            controller.push_frame(valid_frame)

    def test_clear_buffer(self, valid_frame):
        controller = StreamController()
        controller.create_stream()
        
        controller.push_frame(valid_frame)
        controller.clear()
        
        assert controller.buffer.size() == 0
        assert controller.stream.frame_count() == 1 # stream still holds reference
