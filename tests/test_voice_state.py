"""Tests for voice runtime states."""

from __future__ import annotations

from cse.runtime.voice.state import RuntimeState


class TestRuntimeState:
    def test_state_values(self):
        assert RuntimeState.UNINITIALIZED.value == "UNINITIALIZED"
        assert RuntimeState.READY.value == "READY"
        assert RuntimeState.VOICE_LOADED.value == "VOICE_LOADED"
        assert RuntimeState.PROCESSING.value == "PROCESSING"
        assert RuntimeState.SHUTDOWN.value == "SHUTDOWN"
