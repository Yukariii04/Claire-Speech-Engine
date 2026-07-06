"""Tests for AudioFrame and Validation."""

from __future__ import annotations

import uuid
import pytest

from cse.streaming.audio.exceptions import InvalidAudioFrameError
from cse.streaming.audio.frame import AudioFrame
from cse.streaming.audio.validator import validate_frame


class TestAudioFrame:
    def test_audio_frame_creation(self):
        frame = AudioFrame(
            uuid=uuid.uuid4(),
            timestamp_ms=0.0,
            sample_rate=24000,
            channels=1,
            sample_format="PCM_16",
            samples=b"\x00\x00",
            duration_ms=10.0
        )
        assert frame.sample_rate == 24000
        assert frame.sample_format == "PCM_16"
        validate_frame(frame)

    def test_invalid_sample_rate(self):
        frame = AudioFrame(
            uuid=uuid.uuid4(),
            timestamp_ms=0.0,
            sample_rate=0,
            channels=1,
            sample_format="PCM_16",
            samples=b"",
            duration_ms=10.0
        )
        with pytest.raises(InvalidAudioFrameError, match="Invalid sample rate"):
            validate_frame(frame)

    def test_invalid_channels(self):
        frame = AudioFrame(
            uuid=uuid.uuid4(),
            timestamp_ms=0.0,
            sample_rate=24000,
            channels=-1,
            sample_format="PCM_16",
            samples=b"",
            duration_ms=10.0
        )
        with pytest.raises(InvalidAudioFrameError, match="Invalid channels"):
            validate_frame(frame)

    def test_invalid_duration(self):
        frame = AudioFrame(
            uuid=uuid.uuid4(),
            timestamp_ms=0.0,
            sample_rate=24000,
            channels=1,
            sample_format="PCM_16",
            samples=b"",
            duration_ms=-5.0
        )
        with pytest.raises(InvalidAudioFrameError, match="Duration must be positive"):
            validate_frame(frame)

    def test_invalid_samples_type(self):
        frame = AudioFrame(
            uuid=uuid.uuid4(),
            timestamp_ms=0.0,
            sample_rate=24000,
            channels=1,
            sample_format="PCM_16",
            samples="not_bytes", # type: ignore
            duration_ms=10.0
        )
        with pytest.raises(InvalidAudioFrameError, match="Samples must be bytes"):
            validate_frame(frame)
