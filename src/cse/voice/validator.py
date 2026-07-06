"""Voice Package Validator (PRD-007 §8)."""

from __future__ import annotations

from typing import Any
from cse.voice.exceptions import InvalidVoicePackageError
from cse.voice.metadata import VoiceMetadata


def validate_metadata_dict(data: dict[str, Any]) -> None:
    """Validate raw metadata dict from YAML."""
    required_fields = [
        "id", "name", "version", "author", "language",
        "backend", "sample_rate", "channels", "description", "license"
    ]
    
    for field in required_fields:
        if field not in data:
            raise InvalidVoicePackageError(f"Missing required field: {field}")

    if not isinstance(data.get("sample_rate"), int) or data["sample_rate"] <= 0:
        raise InvalidVoicePackageError("sample_rate must be a positive integer")

    if not isinstance(data.get("channels"), int) or data["channels"] <= 0:
        raise InvalidVoicePackageError("channels must be a positive integer")

    if not data.get("id"):
        raise InvalidVoicePackageError("id cannot be empty")
        
    if not data.get("backend"):
        raise InvalidVoicePackageError("backend cannot be empty")
