"""Unit tests for Public API SpeechEngine (PRD-009)."""

import pytest
from pathlib import Path

import cse.voice as _voice_pkg
from cse import SpeechEngine
from cse.api.config import EngineConfig
from cse.api.exceptions import ConfigurationError, SpeechEngineError, VoiceNotLoadedError
from cse.api.lifecycle import EngineState
from cse.runtime.voice.info import BackendVoiceInfo
from cse.voice import VoicePackage, VoiceMetadata, register_voice_package
from cse.voice.registry import PackageRegistry


@pytest.fixture(autouse=True)
def _isolate_voice_registry(monkeypatch):
    """Give each test a fresh PackageRegistry to avoid cross-test leakage."""
    monkeypatch.setattr(_voice_pkg, "_registry", PackageRegistry())


@pytest.fixture
def dummy_voice():
    meta = VoiceMetadata(
        id="test_voice",
        name="Test Voice",
        version="1.0",
        author="Test",
        language="en",
        backend="dummy",
        sample_rate=24000,
        channels=1,
        description="A dummy voice",
        license="MIT"
    )
    pkg = VoicePackage(metadata=meta, path=Path("/tmp/test_voice"))
    register_voice_package(pkg)
    return pkg


class TestSpeechEngine:
    def test_initialization_defaults(self):
        engine = SpeechEngine()
        assert engine._state == EngineState.READY
        assert not engine._voice_loaded

    def test_initialization_with_config_object(self):
        config = EngineConfig(overrides={"foo": "bar"})
        engine = SpeechEngine(config)
        assert engine._config == config

    def test_initialization_with_dict(self):
        engine = SpeechEngine({"foo": "bar"})
        assert isinstance(engine._config, EngineConfig)
        assert engine._config.overrides == {"foo": "bar"}

    def test_initialization_with_path(self):
        engine = SpeechEngine(Path("/fake/config.yaml"))
        assert isinstance(engine._config, EngineConfig)
        assert engine._config.config_path == Path("/fake/config.yaml")

    def test_initialization_invalid_type(self):
        with pytest.raises(ConfigurationError):
            SpeechEngine(config=123)

    def test_lifecycle_shutdown(self):
        engine = SpeechEngine()
        engine.shutdown()
        assert engine._state == EngineState.SHUTDOWN
        
        # Shutdown should be idempotent
        engine.shutdown()
        assert engine._state == EngineState.SHUTDOWN

    def test_operations_after_shutdown_raise(self):
        engine = SpeechEngine()
        engine.shutdown()
        
        with pytest.raises(SpeechEngineError, match="Engine is shut down"):
            engine.load_voice("dummy")
            
        with pytest.raises(SpeechEngineError, match="Engine is shut down"):
            engine.speak("Hello")
            
        with pytest.raises(SpeechEngineError, match="Engine is shut down"):
            engine.list_voices()

    def test_voice_loading(self, dummy_voice):
        engine = SpeechEngine()
        success = engine.load_voice("test_voice")
        assert success is True
        assert engine._voice_loaded is True

    def test_backend_voice_returns_backend_voice_info(self):
        """Backend-validated voices return BackendVoiceInfo through the engine."""
        engine = SpeechEngine()
        engine.load_backend("kittentts")
        assert engine.get_voice() is None

        engine.load_voice("Bella")
        current_voice = engine.get_voice()
        assert current_voice is not None
        assert isinstance(current_voice, BackendVoiceInfo)
        assert not isinstance(current_voice, VoicePackage)
        assert current_voice.metadata.id == "expr-voice-2-f"
        assert current_voice.metadata.name == "Expression 2 Female"
        assert current_voice.metadata.backend == "kittentts"
        assert current_voice.metadata.license is None

        engine.load_backend("dummy")
        assert engine.get_voice() is None
        engine.shutdown()

    def test_voice_loading_fails(self):
        engine = SpeechEngine()
        # PRD-015: use kittentts backend so unknown voices are rejected
        engine.load_backend("kittentts")
        with pytest.raises(SpeechEngineError, match="Failed to load voice"):
            engine.load_voice("does_not_exist")

    def test_speak_without_voice_raises(self):
        engine = SpeechEngine()
        with pytest.raises(VoiceNotLoadedError):
            engine.speak("Hello world")

    def test_speak_generates_error_on_dummy_backend(self, dummy_voice):
        # Dummy backend raises NotImplementedError for synthesize
        engine = SpeechEngine()
        engine.load_voice("test_voice")
        
        with pytest.raises(SpeechEngineError, match="Speech generation failed"):
            engine.speak("Hello world")

    def test_list_voices(self, dummy_voice):
        engine = SpeechEngine()
        # PRD-015: list_voices returns backend voices (dicts), not registry
        engine.load_backend("kittentts")
        voices = engine.list_voices()
        assert isinstance(voices, list)
        ids = [v["id"] for v in voices]
        assert "expr-voice-2-f" in ids

    def test_reload_config(self):
        engine = SpeechEngine()
        engine.reload_config() # should just pass

    def test_get_version(self):
        engine = SpeechEngine()
        assert engine.get_version() == "1.0.5"
