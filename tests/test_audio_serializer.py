"""Tests for StreamSerializer."""

from __future__ import annotations

import uuid
import pytest

from cse.streaming.audio.frame import AudioFrame
from cse.streaming.audio.serializer import StreamSerializer


class TestStreamSerializer:
    def test_serialize_deserialize(self):
        frame = AudioFrame(
            uuid=uuid.uuid4(),
            timestamp_ms=123.4,
            sample_rate=24000,
            channels=1,
            sample_format="PCM_16",
            samples=b"\x01\x02\x03\x04",
            duration_ms=20.5
        )
        
        json_str = StreamSerializer.frame_to_json(frame)
        assert isinstance(json_str, str)
        
        reconstructed = StreamSerializer.json_to_frame(json_str)
        assert reconstructed.uuid == frame.uuid
        assert reconstructed.timestamp_ms == frame.timestamp_ms
        assert reconstructed.sample_rate == frame.sample_rate
        assert reconstructed.channels == frame.channels
        assert reconstructed.sample_format == frame.sample_format
        assert reconstructed.samples == frame.samples
        assert reconstructed.duration_ms == frame.duration_ms
