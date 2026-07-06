"""Performance Events — immutable actions within a Performance Timeline.

Defines the event types and their specific parameters (PRD §9-11, §13).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID


# Event Types (PRD §10)
EVENT_SPEAK_START = "SPEAK_START"
EVENT_TOKEN = "TOKEN"
EVENT_EMPHASIS = "EMPHASIS"
EVENT_PAUSE = "PAUSE"
EVENT_BREATH = "BREATH"
EVENT_SPEAK_END = "SPEAK_END"


# PRD §9
@dataclass(frozen=True)
class PerformanceEvent:
    """An ordered event in the performance timeline."""

    uuid: UUID
    timestamp_ms: int
    event_type: str
    parameters: dict[str, Any]
