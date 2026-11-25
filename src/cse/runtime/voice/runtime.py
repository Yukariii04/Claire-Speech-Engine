"""Voice Runtime orchestrator (PRD-004 §11-14, PRD-015 §10-11)."""

from __future__ import annotations

from cse.performance.graph import PerformanceGraph
from cse.acoustic.backend import AcousticBackend, DummyBackend
from cse.acoustic.backend.exceptions import BackendNotFoundError
from cse.runtime.voice.exceptions import BackendNotRegisteredError, InvalidRuntimeStateError
from cse.runtime.voice.info import BackendVoiceInfo
from cse.runtime.voice.state import RuntimeState
from cse.voice import get_voice_package, VoicePackage, VoicePackageNotFoundError
from cse.voice.metadata import VoiceMetadata


_BACKEND_MAP = {
    "dummy": "cse.acoustic.backend.dummy_backend.DummyBackend",
    "kittentts": "cse.backends.kittentts.backend.KittenTTSBackend",
    "cam": "cse.acoustic.cam.backend.CAMBackend",
}


class VoiceRuntime:
    """Orchestrates the speech pipeline."""

    def __init__(self, backend: AcousticBackend | None = None) -> None:
        self._state = RuntimeState.UNINITIALIZED
        self._backend = backend or DummyBackend()
        self._active_voice: VoicePackage | BackendVoiceInfo | None = None
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
        elif backend_id == "kittentts":
            from cse.backends.kittentts.backend import KittenTTSBackend
            backend = KittenTTSBackend()
        elif backend_id == "cam":
            from cse.acoustic.cam.backend import CAMBackend
            backend = CAMBackend()
        else:
            raise BackendNotFoundError(f"Unknown backend: {backend_id}")
            
        if self._state != RuntimeState.UNINITIALIZED:
            self._backend.shutdown()
            
        self._backend = backend
        self._backend_id = backend_id
        self._active_voice = None  # Reset voice on backend switch
        if self._state == RuntimeState.VOICE_LOADED:
            self._state = RuntimeState.READY
        if self._state != RuntimeState.UNINITIALIZED:
            self._backend.initialize()

    def load_voice(self, voice_id: str) -> None:
        """Load a voice by ID.

        PRD-015 §10-11: First tries the backend's own voice validation.
        Falls back to the VoicePackage registry for backwards compatibility.
        """
        if self._state not in (RuntimeState.READY, RuntimeState.VOICE_LOADED):
            raise InvalidRuntimeStateError(f"Cannot load voice from {self._state}")

        # PRD-015: When the backend enumerates voices, validate against it first
        available = self._backend.list_voices()
        if available:
            if self._backend.validate_voice(voice_id):
                resolved_id = voice_id
                if hasattr(self._backend, "load_voice"):
                    loaded = self._backend.load_voice(voice_id)
                    if isinstance(loaded, str) and loaded:
                        resolved_id = loaded
                self._active_voice = self._build_backend_voice_info(resolved_id, available)
                self._state = RuntimeState.VOICE_LOADED
                return

            # PRD-015 §11: voice doesn't belong to this backend — helpful error
            voice_list = ", ".join(v["id"] for v in available)
            backend_name = self._backend.get_capabilities().backend_name
            from cse.runtime.voice.exceptions import VoiceNotFoundError
            raise VoiceNotFoundError(
                f'Voice "{voice_id}" is not available for {backend_name}.\n'
                f"Available voices: {voice_list}\n"
                f"Run: cse voice"
            )

        # Fallback for backends without enumerated voices (e.g. DummyBackend):
        # resolve from the VoicePackage registry so disk packages stay intact.
        try:
            package = get_voice_package(voice_id)
        except VoicePackageNotFoundError as e:
            from cse.runtime.voice.exceptions import VoiceNotFoundError
            raise VoiceNotFoundError(str(e)) from e

        self._active_voice = package
        self._state = RuntimeState.VOICE_LOADED

    def _build_backend_voice_info(
        self,
        voice_id: str,
        available: list[dict[str, str]],
    ) -> BackendVoiceInfo:
        """Build a BackendVoiceInfo from the backend's capabilities and voice entry."""
        caps = self._backend.get_capabilities()
        vid_lower = voice_id.strip().lower()
        matched = next(
            (
                v
                for v in available
                if v.get("id", "").lower() == vid_lower
                or v.get("alias", "").lower() == vid_lower
                or v.get("name", "").lower() == vid_lower
            ),
            None,
        )
        resolved_id = matched["id"] if matched and "id" in matched else voice_id
        display_name = matched.get("name", resolved_id) if matched else resolved_id
        language = matched.get("language") or (
            caps.supported_languages[0] if caps.supported_languages else "en"
        )
        metadata = VoiceMetadata(
            id=resolved_id,
            name=display_name,
            version=caps.backend_version,
            author=caps.backend_name,
            language=language,
            backend=self._backend_id,
            sample_rate=caps.sample_rate,
            channels=1,
            description=f"{caps.backend_name} voice '{display_name}'",
            license=None,  # Backends do not supply license info
        )
        return BackendVoiceInfo(metadata=metadata)

    def unload_voice(self) -> None:
        """Unload the currently active voice."""
        if self._state == RuntimeState.VOICE_LOADED:
            self._active_voice = None
            self._state = RuntimeState.READY

    def process(self, graph: PerformanceGraph) -> object:
        """Process a performance graph and return synthesized audio."""
        if self._state != RuntimeState.VOICE_LOADED:
            raise InvalidRuntimeStateError(f"Cannot process from {self._state}")
        
        if not self._backend:
            raise BackendNotRegisteredError("No backend registered")

        self._state = RuntimeState.PROCESSING
        try:
            # Backend now implements BaseTranslator
            return self._backend.process(graph)
        finally:
            self._state = RuntimeState.VOICE_LOADED

    def get_loaded_voice(self) -> VoicePackage | BackendVoiceInfo | None:
        """Get the currently loaded voice (VoicePackage or BackendVoiceInfo)."""
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
