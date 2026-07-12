"""Voice Runtime orchestrator (PRD-004 §11-14, PRD-015 §10-11)."""

from __future__ import annotations

from cse.performance.compiler.timeline import PerformanceTimeline
from cse.acoustic.backend import AcousticBackend, DummyBackend
from cse.acoustic.backend.exceptions import BackendNotFoundError
from cse.runtime.voice.exceptions import BackendNotRegisteredError, InvalidRuntimeStateError
from cse.runtime.voice.state import RuntimeState
from cse.voice import get_voice_package, VoicePackage, VoicePackageNotFoundError


# ponytail: map of known backend IDs, no registry class needed
_BACKEND_MAP = {
    "dummy": "cse.acoustic.backend.dummy_backend.DummyBackend",
    "kokoro": "cse.backends.kokoro.backend.KokoroBackend",
    "fishspeech": "cse.backends.fishspeech.backend.FishSpeechBackend",
    "styletts2": "cse.backends.styletts2.backend.StyleTTS2Backend",
}


class VoiceRuntime:
    """Orchestrates the speech pipeline."""

    def __init__(self, backend: AcousticBackend | None = None) -> None:
        self._state = RuntimeState.UNINITIALIZED
        self._backend = backend or DummyBackend()
        self._active_voice: VoicePackage | None = None
        self._backend_id: str = "dummy"

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
        elif backend_id == "fishspeech":
            from cse.backends.fishspeech.backend import FishSpeechBackend
            backend = FishSpeechBackend()
        elif backend_id == "styletts2":
            from cse.backends.styletts2.backend import StyleTTS2Backend
            backend = StyleTTS2Backend()
        else:
            raise BackendNotFoundError(f"Unknown backend: {backend_id}")
            
        if self._state != RuntimeState.UNINITIALIZED:
            self._backend.shutdown()
            
        self._backend = backend
        self._backend_id = backend_id
        if self._state != RuntimeState.UNINITIALIZED:
            self._backend.initialize()

    def load_voice(self, voice_id: str) -> None:
        """Load a voice by ID.

        PRD-015 §10-11: First tries the backend's own voice validation.
        Falls back to the VoicePackage registry for backwards compatibility.
        """
        if self._state not in (RuntimeState.READY, RuntimeState.VOICE_LOADED):
            raise InvalidRuntimeStateError(f"Cannot load voice from {self._state}")

        # PRD-015: Let the backend validate the voice first
        if self._backend.validate_voice(voice_id):
            # ponytail: backend owns this voice, tell it to load directly
            if hasattr(self._backend, 'load_voice'):
                self._backend.load_voice(voice_id)
            self._active_voice = None  # No VoicePackage needed
            self._state = RuntimeState.VOICE_LOADED
            return

        # PRD-015 §11: voice doesn't belong to this backend — helpful error
        available = self._backend.list_voices()
        if available:
            voice_list = ", ".join(v["id"] for v in available)
            backend_name = self._backend.get_capabilities().backend_name
            from cse.runtime.voice.exceptions import VoiceNotFoundError
            raise VoiceNotFoundError(
                f'Voice "{voice_id}" is not available for {backend_name}.\n'
                f"Available voices: {voice_list}\n"
                f"Run: cse voices"
            )

        # Fallback: try VoicePackage registry (backwards compat)
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

    def get_backend_id(self) -> str:
        """Return the current backend ID."""
        return self._backend_id

    def get_backend(self) -> AcousticBackend:
        """Return the current backend instance."""
        return self._backend

    @staticmethod
    def available_backend_ids() -> list[str]:
        """Return all known backend IDs."""
        return [k for k in _BACKEND_MAP if k != "dummy"]
