"""Tests for VoiceRuntime (PRD-004 §15 / PRD-007)."""

from __future__ import annotations

import pytest

from cse.performance.compiler.timeline import PerformanceTimeline, PerformanceMetadata
from cse.runtime.voice.exceptions import InvalidRuntimeStateError, VoiceNotFoundError
from cse.runtime.voice.runtime import VoiceRuntime
from cse.voice import register_voice_package, VoicePackage, VoiceMetadata
from pathlib import Path
import uuid


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
        
        voice = runtime.get_loaded_voice()
        assert voice is not None
        assert voice.metadata.name == "Claire"
        
        runtime.unload_voice()
        assert runtime.get_loaded_voice() is None

    def test_load_voice_uninitialized_raises(self, mock_package):
        runtime = VoiceRuntime()
        
        with pytest.raises(InvalidRuntimeStateError):
            runtime.load_voice("claire")

    def test_unknown_voice_raises(self):
        runtime = VoiceRuntime()
        runtime.initialize()
        
        with pytest.raises(VoiceNotFoundError):
            runtime.load_voice("unknown_voice_id_never_registered")

    def test_process_raises_not_implemented(self, mock_package):
        runtime = VoiceRuntime()
        runtime.initialize()
        try:
            register_voice_package(mock_package)
        except Exception:
            pass # already registered globally in this test run
            
        runtime.load_voice("claire")
        
        tl = PerformanceTimeline(
            uuid=uuid.uuid4(),
            version="1.0.0",
            events=(),
            metadata=PerformanceMetadata()
        )
        
        with pytest.raises(NotImplementedError, match="Dummy backend does not synthesize"):
            runtime.process(tl)
            
    def test_process_without_voice_raises(self):
        runtime = VoiceRuntime()
        runtime.initialize()
        
        tl = PerformanceTimeline(
            uuid=uuid.uuid4(),
            version="1.0.0",
            events=(),
            metadata=PerformanceMetadata()
        )
        
        with pytest.raises(InvalidRuntimeStateError):
            runtime.process(tl)
