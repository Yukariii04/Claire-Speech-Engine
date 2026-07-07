"""Public Speech Engine API (PRD-009 §4)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from cse.api.config import EngineConfig
from cse.api.exceptions import (
    ConfigurationError,
    SpeechEngineError,
    VoiceNotLoadedError,
)
from cse.api.lifecycle import EngineState
from cse.language.cir.builder import build_cir
from cse.performance.compiler import compile_performance
from cse.runtime.voice.runtime import VoiceRuntime
from cse.voice import list_voice_packages


class SpeechEngine:
    """The main entry point for The Claire Speech Engine."""

    def __init__(self, config: EngineConfig | dict | str | Path | None = None) -> None:
        """Initialize the SpeechEngine with an optional configuration."""
        self._config = self._resolve_config(config)
        self._runtime = VoiceRuntime()
        self._runtime.initialize()
        self._state = EngineState.READY
        self._voice_loaded = False

    def _resolve_config(self, config: Any) -> EngineConfig:
        """Resolve varying config input types into an EngineConfig."""
        if isinstance(config, EngineConfig):
            return config
        if isinstance(config, (str, Path)):
            return EngineConfig(config_path=Path(config))
        if isinstance(config, dict):
            return EngineConfig(overrides=config)
        if config is None:
            return EngineConfig()
        raise ConfigurationError("Invalid configuration type provided.")

    def load_voice(self, voice_id: str) -> bool:
        """Load a voice by ID."""
        self._check_state()
        try:
            self._runtime.load_voice(voice_id)
            self._voice_loaded = True
            return True
        except Exception as e:
            raise SpeechEngineError(f"Failed to load voice {voice_id}: {e}") from e

    def get_voice(self) -> Any:
        """Get the currently loaded voice package."""
        self._check_state()
        return self._runtime.get_loaded_voice()

    def list_voices(self) -> list[str]:
        """List all available voice package IDs."""
        self._check_state()
        return list_voice_packages()

    def load_backend(self, backend_id: str) -> None:
        """Load an acoustic backend."""
        self._check_state()
        self._runtime.load_backend(backend_id)

    def get_backend_capabilities(self) -> dict[str, Any]:
        """Get capabilities of the current backend."""
        self._check_state()
        caps = self._runtime._backend.get_capabilities()
        return caps.__dict__ if hasattr(caps, "__dict__") else {}

    def speak(self, text: str) -> Any:
        """Generate speech from text.
        
        Orchestrates: Text -> CIR -> Timeline -> Runtime -> Backend -> Result.
        """
        self._check_state()
        if not self._voice_loaded:
            raise VoiceNotLoadedError("Cannot speak without loading a voice first.")
        
        try:
            cir = build_cir(text)
            timeline = compile_performance(cir)
            return self._runtime.process(timeline)
        except Exception as e:
            raise SpeechEngineError(f"Speech generation failed: {e}") from e

    def reload_config(self) -> None:
        """Reload the engine configuration."""
        self._check_state()
        # Minimal implementation for PRD-009
        pass

    def get_version(self) -> str:
        """Return the engine version."""
        return "1.0.0"

    def shutdown(self) -> None:
        """Safely shutdown the engine and release resources. Idempotent."""
        if self._state == EngineState.SHUTDOWN:
            return
        self._runtime.shutdown()
        self._voice_loaded = False
        self._state = EngineState.SHUTDOWN

    def _check_state(self) -> None:
        """Ensure the engine is ready to receive commands."""
        if self._state == EngineState.SHUTDOWN:
            raise SpeechEngineError("Engine is shut down.")
