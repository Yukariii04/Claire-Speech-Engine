"""Voice Runtime State (PRD-004 §6)."""

from __future__ import annotations

from enum import Enum


class RuntimeState(Enum):
    """States of the VoiceRuntime."""
    
    UNINITIALIZED = "UNINITIALIZED"
    READY = "READY"
    VOICE_LOADED = "VOICE_LOADED"
    PROCESSING = "PROCESSING"
    SHUTDOWN = "SHUTDOWN"
