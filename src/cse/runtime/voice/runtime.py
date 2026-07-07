"""Voice Runtime orchestrator (PRD-004 §11-14)."""

from __future__ import annotations

from cse.performance.compiler.timeline import PerformanceTimeline
from cse.acoustic.backend import AcousticBackend, DummyBackend
from cse.acoustic.backend.exceptions import BackendNotFoundError
from cse.runtime.voice.exceptions import BackendNotRegisteredError, InvalidRuntimeStateError
from cse.runtime.voice.state import RuntimeState
from cse.voice import get_voice_package, VoicePackage, VoicePackageNotFoundError


class VoiceRuntime:
    """Orchestrates the speech pipeline."""

    def __init__(self, backend: AcousticBackend | None = None) -> None:
        self._state = RuntimeState.UNINITIALIZED
        self._backend = backend or DummyBackend()
        self._active_voice: VoicePackage | None = None

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
        
        self.unload_voice()
        self._backend.shutdown()
        self._state = RuntimeState.SHUTDOWN

    def load_backend(self, backend_id: str) -> None:
        """Switch the acoustic backend by ID."""
        if backend_id == "dummy":
            from cse.acoustic.backend.dummy_backend import DummyBackend
            backend = DummyBackend()
        elif backend_id == "kokoro":
            from cse.backends.kokoro.backend import KokoroBackend
            backend = KokoroBackend()
        else:
            raise BackendNotFoundError(f"Unknown backend: {backend_id}")
            
        if self._state != RuntimeState.UNINITIALIZED:
            self._backend.shutdown()
            
        self._backend = backend
        if self._state != RuntimeState.UNINITIALIZED:
            self._backend.initialize()

    def load_voice(self, voice_id: str) -> None:
        """Load a voice by ID."""
        if self._state not in (RuntimeState.READY, RuntimeState.VOICE_LOADED):
            raise InvalidRuntimeStateError(f"Cannot load voice from {self._state}")

        # PRD-007: Use Voice Package System
        try:
            package = get_voice_package(voice_id)
        except VoicePackageNotFoundError as e:
            from cse.runtime.voice.exceptions import VoiceNotFoundError
            raise VoiceNotFoundError(str(e)) from e
            
        self._active_voice = package
        self._state = RuntimeState.VOICE_LOADED

    def unload_voice(self) -> None:
        """Unload the currently active voice."""
        if self._state == RuntimeState.VOICE_LOADED:
            self._active_voice = None
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

    def get_loaded_voice(self) -> VoicePackage | None:
        """Get the currently loaded VoicePackage."""
        return self._active_voice
