"""Tests for AudioStream."""

from __future__ import annotations

import uuid
import pytest

from cse.streaming.audio.exceptions import ClosedStreamError
from cse.streaming.audio.frame import AudioFrame
from cse.streaming.audio.stream import AudioStream


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


class TestAudioStream:
    def test_stream_creation(self):
        stream = AudioStream()
        assert stream.frame_count() == 0
        assert stream.duration() == 0.0
        assert stream.closed is False

    def test_append_frame(self, valid_frame):
        stream = AudioStream()
        stream.append(valid_frame)
        assert stream.frame_count() == 1
        assert stream.duration() == 10.0

    def test_close_stream(self, valid_frame):
        stream = AudioStream()
        stream.append(valid_frame)
        stream.close()
        
        assert stream.closed is True
        
        with pytest.raises(ClosedStreamError):
            stream.append(valid_frame)
