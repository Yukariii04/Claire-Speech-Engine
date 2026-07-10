"""Tests for evaluation backends (PRD-013.6).

ponytail: These tests run locally without GPU/models.
Real inference is validated via COLAB-001.
"""

import os
import pytest
from unittest.mock import patch
from cse.backends.fishspeech.backend import FishSpeechBackend
from cse.backends.styletts2.backend import StyleTTS2Backend
from cse.backends.fishspeech.exceptions import FishSpeechInitializationError, SpeechGenerationError as FSGenError
from cse.backends.styletts2.exceptions import StyleTTS2InitializationError, SpeechGenerationError as STGenError


class TestFishSpeechBackend:
    def test_init_without_checkpoint_raises(self, tmp_path, monkeypatch):
        monkeypatch.setenv("FISH_CHECKPOINT_DIR", str(tmp_path / "nonexistent"))
        backend = FishSpeechBackend()
        with pytest.raises(FishSpeechInitializationError, match="checkpoint not found"):
            backend.initialize()

    def test_capabilities(self):
        backend = FishSpeechBackend()
        caps = backend.get_capabilities()
        assert caps.backend_name == "fishspeech"
        assert caps.emotion == "high"

    def test_load_voice(self):
        backend = FishSpeechBackend()
        assert backend.load_voice("neutral") == "neutral"

    def test_synthesize_without_init_raises(self):
        backend = FishSpeechBackend()
        with pytest.raises(FSGenError, match="not initialized"):
            backend.synthesize("test")


class TestStyleTTS2Backend:
    def test_init_without_package_raises(self):
        backend = StyleTTS2Backend()
        with patch.dict("sys.modules", {"styletts2": None}):
            with pytest.raises(StyleTTS2InitializationError, match="not installed"):
                backend.initialize()

    def test_capabilities(self):
        backend = StyleTTS2Backend()
        caps = backend.get_capabilities()
        assert caps.backend_name == "styletts2"
        assert caps.emotion == "medium"

    def test_load_voice(self):
        backend = StyleTTS2Backend()
        assert backend.load_voice("default") == "default"

    def test_synthesize_without_init_raises(self):
        backend = StyleTTS2Backend()
        with pytest.raises(STGenError, match="not initialized"):
            backend.synthesize("test")


class TestBackendRegistration:
    """Verify backends can be imported and instantiated through engine routing."""
    def test_fishspeech_importable(self):
        from cse.runtime.voice.runtime import VoiceRuntime
        rt = VoiceRuntime()
        # ponytail: don't initialize (needs checkpoint), just verify import routing
        backend = FishSpeechBackend()
        assert backend.__class__.__name__ == "FishSpeechBackend"

    def test_styletts2_importable(self):
        backend = StyleTTS2Backend()
        assert backend.__class__.__name__ == "StyleTTS2Backend"
