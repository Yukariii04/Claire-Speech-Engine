"""Tests for VoiceRuntime (PRD-004 §15)."""

from __future__ import annotations

import pytest
import yaml

from cse.performance.compiler.timeline import PerformanceTimeline, PerformanceMetadata
from cse.runtime.voice.exceptions import InvalidRuntimeStateError, VoiceNotFoundError
from cse.runtime.voice.manager import VoiceManager
from cse.runtime.voice.runtime import VoiceRuntime
import uuid


@pytest.fixture
def mock_voice_dir(tmp_path):
    voice_dir = tmp_path / "claire"
    voice_dir.mkdir(parents=True)
    meta_file = voice_dir / "metadata.yaml"
    with open(meta_file, "w") as f:
        yaml.dump({"id": "claire", "name": "Claire"}, f)
    return str(tmp_path)


class TestVoiceRuntime:
    def test_initialization(self):
        runtime = VoiceRuntime()
        # Should start uninitialized and transition to ready
        runtime.initialize()
        
        # Second init should fail
        with pytest.raises(InvalidRuntimeStateError):
            runtime.initialize()

    def test_shutdown(self):
        runtime = VoiceRuntime()
        runtime.initialize()
        runtime.shutdown()
        
        # Can shutdown again safely (idempotent per typical shutdown patterns) or UNINITIALIZED
        runtime.shutdown()

    def test_load_and_unload_voice(self, mock_voice_dir):
        manager = VoiceManager(voices_dir=mock_voice_dir)
        runtime = VoiceRuntime(manager=manager)
        
        runtime.initialize()
        runtime.load_voice("claire")
        
        voice = runtime.get_loaded_voice()
        assert voice is not None
        assert voice["name"] == "Claire"
        
        runtime.unload_voice()
        assert runtime.get_loaded_voice() is None

    def test_load_voice_uninitialized_raises(self, mock_voice_dir):
        manager = VoiceManager(voices_dir=mock_voice_dir)
        runtime = VoiceRuntime(manager=manager)
        
        with pytest.raises(InvalidRuntimeStateError):
            runtime.load_voice("claire")

    def test_unknown_voice_raises(self, mock_voice_dir):
        manager = VoiceManager(voices_dir=mock_voice_dir)
        runtime = VoiceRuntime(manager=manager)
        runtime.initialize()
        
        with pytest.raises(VoiceNotFoundError):
            runtime.load_voice("unknown")

    def test_process_raises_not_implemented(self, mock_voice_dir):
        # PRD §18 Example
        manager = VoiceManager(voices_dir=mock_voice_dir)
        runtime = VoiceRuntime(manager=manager)
        
        runtime.initialize()
        runtime.load_voice("claire")
        
        tl = PerformanceTimeline(
            uuid=uuid.uuid4(),
            version="1.0.0",
            events=(),
            metadata=PerformanceMetadata()
        )
        
        # Dummy backend raises NotImplementedError
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
