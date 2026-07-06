"""Public API Lifecycle (PRD-009 §9)."""

from __future__ import annotations


class EngineState:
    """Tracks the lifecycle state of the SpeechEngine."""
    UNINITIALIZED = "UNINITIALIZED"
    READY = "READY"
    SHUTDOWN = "SHUTDOWN"
