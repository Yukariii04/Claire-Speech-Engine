"""Tests for VoiceRuntime (PRD-004 §15 / PRD-007)."""

from __future__ import annotations

import pytest

import cse.voice as _voice_pkg
from cse.performance.graph import PerformanceGraph
from cse.runtime.voice.exceptions import InvalidRuntimeStateError, VoiceNotFoundError
from cse.runtime.voice.info import BackendVoiceInfo
from cse.runtime.voice.runtime import VoiceRuntime
from cse.voice import register_voice_package, VoicePackage, VoiceMetadata
from cse.voice.registry import PackageRegistry
from pathlib import Path


@pytest.fixture(autouse=True)
def _isolate_voice_registry(monkeypatch):
    """Give each test a fresh PackageRegistry to avoid cross-test leakage."""
    monkeypatch.setattr(_voice_pkg, "_registry", PackageRegistry())


@pytest.fixture
def mock_package():
    meta = VoiceMetadata(
        id="claire",
        name="Claire",
        version="1.0.0",
        author="Test",
        language="en",
        backend="dummy",
        sample_rate=24000,
        channels=1,
        description="Test",
        license="MIT"
    )
    return VoicePackage(metadata=meta, path=Path("/tmp/claire"))


class TestVoiceRuntime:
    def test_initialization(self):
        runtime = VoiceRuntime()
        runtime.initialize()
        
        with pytest.raises(InvalidRuntimeStateError):
            runtime.initialize()

    def test_shutdown(self):
        runtime = VoiceRuntime()
        runtime.initialize()
        runtime.shutdown()
        
        runtime.shutdown()

    def test_load_and_unload_voice(self, mock_package):
        register_voice_package(mock_package)
        runtime = VoiceRuntime()
        
        runtime.initialize()
        runtime.load_voice("claire")
        
        # PRD-015: backend-native voices may not populate VoicePackage
        from cse.runtime.voice.state import RuntimeState
        assert runtime._state == RuntimeState.VOICE_LOADED
        
        runtime.unload_voice()
        assert runtime._state == RuntimeState.READY

    def test_backend_voice_returns_backend_voice_info(self):
        """Backend-validated voices return BackendVoiceInfo, not VoicePackage."""
        runtime = VoiceRuntime()
        runtime.initialize()
        runtime.load_backend("kittentts")
        runtime.load_voice("Bella")

        loaded = runtime.get_loaded_voice()
        assert loaded is not None
        assert isinstance(loaded, BackendVoiceInfo)
        assert not isinstance(loaded, VoicePackage)
        assert loaded.metadata.id == "expr-voice-2-f"
        assert loaded.metadata.name == "Expression 2 Female"
        assert loaded.metadata.backend == "kittentts"
        assert loaded.metadata.license is None
        assert not hasattr(loaded, "path")

        runtime.load_backend("dummy")
        assert runtime.get_loaded_voice() is None
        runtime.shutdown()

    def test_load_voice_uninitialized_raises(self, mock_package):
        runtime = VoiceRuntime()
        
        with pytest.raises(InvalidRuntimeStateError):
            runtime.load_voice("claire")

    def test_unknown_voice_raises(self):
        runtime = VoiceRuntime()
        runtime.initialize()
        # PRD-015: use a backend with a voice list so validation rejects unknowns
        runtime.load_backend("kittentts")
        
        with pytest.raises(VoiceNotFoundError):
            runtime.load_voice("unknown_voice_id_never_registered")

    def test_process_raises_not_implemented(self, mock_package):
        runtime = VoiceRuntime()
        runtime.initialize()
        register_voice_package(mock_package)
            
        runtime.load_voice("claire")
        
        tl = PerformanceGraph(
            text="test", character_state=None, semantics={}, intent={}, plan={}
        )
        
        with pytest.raises(NotImplementedError, match="Dummy backend does not synthesize"):
            runtime.process(tl)
            
    def test_process_without_voice_raises(self):
        runtime = VoiceRuntime()
        runtime.initialize()
        
        tl = PerformanceGraph(
            text="test", character_state=None, semantics={}, intent={}, plan={}
        )
        
        with pytest.raises(InvalidRuntimeStateError):
            runtime.process(tl)
