"""Voice Runtime orchestrator (PRD-004 §11-14)."""

from __future__ import annotations

from cse.performance.compiler.timeline import PerformanceTimeline
from cse.acoustic.backend import AcousticBackend, DummyBackend
from cse.runtime.voice.exceptions import BackendNotRegisteredError, InvalidRuntimeStateError
from cse.runtime.voice.manager import VoiceManager
from cse.runtime.voice.state import RuntimeState


class VoiceRuntime:
    """Orchestrates the speech pipeline."""

    def __init__(self, manager: VoiceManager | None = None, backend: AcousticBackend | None = None) -> None:
        self._state = RuntimeState.UNINITIALIZED
        self._manager = manager or VoiceManager()
        self._backend = backend or DummyBackend()

    def initialize(self) -> None:
        """Initialize the runtime."""
        if self._state != RuntimeState.UNINITIALIZED:
            raise InvalidRuntimeStateError(f"Cannot initialize from {self._state}")
        
        self._backend.initialize()
        self._state = RuntimeState.READY

    def shutdown(self) -> None:
        """Shutdown the runtime."""
        if self._state == RuntimeState.UNINITIALIZED:
            return
        
        self._manager.unload_voice()
        self._backend.shutdown()
        self._state = RuntimeState.SHUTDOWN

    def load_voice(self, voice_id: str) -> None:
        """Load a voice by ID."""
        if self._state not in (RuntimeState.READY, RuntimeState.VOICE_LOADED):
            raise InvalidRuntimeStateError(f"Cannot load voice from {self._state}")

        self._manager.load_voice(voice_id)
        self._state = RuntimeState.VOICE_LOADED

    def unload_voice(self) -> None:
        """Unload the currently active voice."""
        if self._state != RuntimeState.VOICE_LOADED:
            raise InvalidRuntimeStateError(f"Cannot unload voice from {self._state}")

        self._manager.unload_voice()
        self._state = RuntimeState.READY

    def process(self, timeline: PerformanceTimeline) -> object:
        """Process a timeline and return synthesized audio."""
        if self._state != RuntimeState.VOICE_LOADED:
            raise InvalidRuntimeStateError(f"Cannot process from {self._state}")
        
        if not self._backend:
            raise BackendNotRegisteredError("No backend registered")

        self._state = RuntimeState.PROCESSING
        try:
            # For PRD-004, dummy backend will raise NotImplementedError
            return self._backend.synthesize(timeline)
        finally:
            self._state = RuntimeState.VOICE_LOADED

    def get_loaded_voice(self) -> dict[str, str] | None:
        """Get the currently loaded voice metadata."""
        return self._manager.get_loaded_voice()
