"""Stream Serializer."""

from __future__ import annotations

import base64
import json
from typing import Any

from cse.streaming.audio.frame import AudioFrame
import uuid


class StreamSerializer:
    """Serializes AudioFrames to/from dict/JSON."""

    @staticmethod
    def frame_to_dict(frame: AudioFrame) -> dict[str, Any]:
        """Serialize an AudioFrame to a dictionary."""
        return {
            "uuid": str(frame.uuid),
            "timestamp_ms": frame.timestamp_ms,
            "sample_rate": frame.sample_rate,
            "channels": frame.channels,
            "sample_format": frame.sample_format,
            "samples_b64": base64.b64encode(frame.samples).decode('utf-8'),
            "duration_ms": frame.duration_ms,
        }

    @staticmethod
    def dict_to_frame(data: dict[str, Any]) -> AudioFrame:
        """Deserialize a dictionary to an AudioFrame."""
        return AudioFrame(
            uuid=uuid.UUID(data["uuid"]),
            timestamp_ms=float(data["timestamp_ms"]),
            sample_rate=int(data["sample_rate"]),
            channels=int(data["channels"]),
            sample_format=str(data["sample_format"]),
            samples=base64.b64decode(data["samples_b64"]),
            duration_ms=float(data["duration_ms"])
        )

    @classmethod
    def frame_to_json(cls, frame: AudioFrame) -> str:
        """Serialize an AudioFrame to a JSON string."""
        return json.dumps(cls.frame_to_dict(frame))

    @classmethod
    def json_to_frame(cls, json_str: str) -> AudioFrame:
        """Deserialize a JSON string to an AudioFrame."""
        return cls.dict_to_frame(json.loads(json_str))
