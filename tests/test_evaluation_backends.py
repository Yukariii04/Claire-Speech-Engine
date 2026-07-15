"""Tests for evaluation backends (PRD-013.6).

ponytail: These tests run locally without GPU/models.
Real inference is validated via COLAB-001.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from cse.backends.styletts2.backend import StyleTTS2Backend
from cse.backends.styletts2.exceptions import StyleTTS2InitializationError, SpeechGenerationError as STGenError


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

    def test_translate_without_init_raises(self):
        backend = StyleTTS2Backend()
        with pytest.raises(STGenError, match="not initialized"):
            backend.translate(MagicMock(text="test"))

    def test_translate_passes_target_voice_path(self, tmp_path):
        from unittest.mock import MagicMock
        import numpy as np
        
        backend = StyleTTS2Backend()
        backend._initialized = True
        backend.load_voice("claire_neutral")
        
        backend._ensure_model = MagicMock()
        backend._tts = MagicMock()
        backend._tts.inference.return_value = np.zeros(24000, dtype=np.float32)
        
        # Test synthesis
        res = backend.translate(MagicMock(text="hello world"))
        
        # Verify the actual call
        backend._tts.inference.assert_called_once()
        args, kwargs = backend._tts.inference.call_args
        assert args[0] == "hello world"
        assert "target_voice_path" in kwargs
        assert "claire_neutral.wav" in str(kwargs["target_voice_path"])
        assert res.success is True


class TestBackendRegistration:
    """Verify backends can be imported and instantiated through engine routing."""
    def test_styletts2_importable(self):
        backend = StyleTTS2Backend()
        assert backend.__class__.__name__ == "StyleTTS2Backend"
