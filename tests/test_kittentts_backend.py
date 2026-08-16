"""Tests for KittenTTS Backend.

Split into:
  - Unit tests: No model download required (mocked inference, config, result, exceptions).
  - Integration tests: End-to-end real synthesis.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from cse.backends.kittentts.backend import KittenTTSBackend
from cse.backends.kittentts.config import KittenTTSConfig
from cse.backends.kittentts.exceptions import (
    KittenTTSBackendError,
    KittenTTSInitializationError,
    SpeechGenerationError,
    VoiceLoadError,
)
from cse.backends.kittentts.result import SpeechResult
from cse.performance.graph import PerformanceGraph


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def simple_graph():
    """A graph with spoken text."""
    return PerformanceGraph(
        text="Hello world",
        character_state=None,
        semantics={},
        intent={},
        plan={"delivery": {"pace": "moderate"}},
    )


@pytest.fixture
def fast_graph():
    """A graph with fast pace."""
    return PerformanceGraph(
        text="Hurry up!",
        character_state=None,
        semantics={},
        intent={"primary_intent": "exclamation"},
        plan={"delivery": {"pace": "fast", "pitch_contour": "peaked", "emphasis": "throughout"}},
    )


@pytest.fixture
def empty_graph():
    """A graph with no spoken text."""
    return PerformanceGraph(
        text="",
        character_state=None,
        semantics={},
        intent={},
        plan={},
    )


# ─── Exception Tests ─────────────────────────────────────────────────────────

class TestExceptions:
    def test_exception_hierarchy(self):
        assert issubclass(KittenTTSBackendError, Exception)
        assert issubclass(KittenTTSInitializationError, KittenTTSBackendError)
        assert issubclass(VoiceLoadError, KittenTTSBackendError)
        assert issubclass(SpeechGenerationError, KittenTTSBackendError)


# ─── Config Tests ─────────────────────────────────────────────────────────────

class TestKittenTTSConfig:
    def test_default_config(self):
        config = KittenTTSConfig()
        assert config.model_name == "KittenML/kitten-tts-nano-0.8"
        assert config.sample_rate == 24000
        assert config.default_voice == "expr-voice-2-f"
        assert config.default_speed == 1.0
        assert config.output_dir == "outputs/kittentts"

    def test_custom_config(self):
        config = KittenTTSConfig(
            model_name="KittenML/kitten-tts-mini-0.8",
            default_voice="expr-voice-2-m",
            default_speed=1.2,
            output_dir="custom_output",
        )
        assert config.model_name == "KittenML/kitten-tts-mini-0.8"
        assert config.default_voice == "expr-voice-2-m"
        assert config.default_speed == 1.2
        assert config.output_dir == "custom_output"


# ─── SpeechResult Tests ──────────────────────────────────────────────────────

class TestSpeechResult:
    def test_immutable(self):
        result = SpeechResult(
            success=True,
            audio_path=Path("/tmp/test.wav"),
            duration_seconds=1.5,
            sample_rate=24000,
            channels=1,
            backend="kittentts",
            voice="expr-voice-2-f",
            metadata={"text": "hello"},
        )
        assert result.success is True
        assert result.backend == "kittentts"
        assert result.sample_rate == 24000
        with pytest.raises(Exception):
            result.success = False


# ─── Backend Unit Tests ──────────────────────────────────────────────────────

class TestKittenTTSBackendUnit:
    def test_initialize_missing_import(self):
        backend = KittenTTSBackend()
        with patch.dict("sys.modules", {"kittentts": None}):
            with pytest.raises(KittenTTSInitializationError, match="not installed"):
                backend.initialize()

    def test_translate_without_init(self, simple_graph):
        backend = KittenTTSBackend()
        with pytest.raises(SpeechGenerationError, match="not initialized"):
            backend.translate(simple_graph)

    def test_translate_empty_text(self, empty_graph):
        backend = KittenTTSBackend()
        backend.initialize()
        backend._ensure_model = MagicMock()
        with pytest.raises(SpeechGenerationError, match="no spoken text"):
            backend.translate(empty_graph)

    def test_shutdown(self):
        backend = KittenTTSBackend()
        backend.initialize()
        assert backend._initialized is True
        backend.shutdown()
        assert backend._initialized is False
        assert backend._model is None
        assert backend._voice is None

    def test_load_voice(self):
        backend = KittenTTSBackend()
        assert backend.load_voice("expr-voice-2-f") == "expr-voice-2-f"
        assert backend.load_voice("expr-voice-3-m") == "expr-voice-3-m"
        assert backend.load_voice(None) == "expr-voice-2-f"

    def test_load_voice_alias(self):
        backend = KittenTTSBackend()
        assert backend.load_voice("Bella") == "expr-voice-2-f"
        assert backend.load_voice("jasper") == "expr-voice-2-m"
        assert backend.load_voice("Leo") == "expr-voice-5-m"

    def test_load_voice_invalid_raises(self):
        backend = KittenTTSBackend()
        with pytest.raises(VoiceLoadError, match="not valid"):
            backend.load_voice("invalid_voice_name")

    def test_get_capabilities(self):
        backend = KittenTTSBackend()
        caps = backend.get_capabilities()
        assert caps.backend_name == "kittentts"
        assert caps.supports_streaming is False
        assert caps.supports_batch is False
        assert caps.supports_multispeaker is False
        assert caps.supports_voice_cloning is False
        assert caps.emotion == "limited"
        assert caps.sample_rate == 24000
        assert caps.requires_gpu is False
        assert "en" in caps.supported_languages
        assert caps.backend_version == "0.8.1"

    def test_list_voices(self):
        backend = KittenTTSBackend()
        voices = backend.list_voices()
        assert len(voices) == 8
        ids = [v["id"] for v in voices]
        assert "expr-voice-2-f" in ids
        assert "expr-voice-2-m" in ids
        aliases = [v["alias"] for v in voices]
        assert "Bella" in aliases
        assert "Jasper" in aliases

    def test_list_models(self):
        from cse.backends.kittentts.backend import list_models
        models = list_models()
        assert len(models) == 3
        ids = [m["id"] for m in models]
        assert "kitten-tts-nano-0.8" in ids
        assert "kitten-tts-micro-0.8" in ids
        assert "kitten-tts-mini-0.8" in ids
        assert "kitten-tts-nano-0.1" not in ids

    def test_validate_model(self):
        from cse.backends.kittentts.backend import validate_model
        assert validate_model("kitten-tts-nano-0.8") is True
        assert validate_model("kitten-tts-micro-0.8") is True
        assert validate_model("KittenML/kitten-tts-mini-0.8") is True
        assert validate_model("kitten-tts-nano-0.1") is False
        assert validate_model("invalid-model-name") is False
        assert validate_model("") is False

    def test_resolve_model_repo_id(self):
        from cse.backends.kittentts.backend import resolve_model_repo_id
        assert resolve_model_repo_id("kitten-tts-nano-0.8") == "KittenML/kitten-tts-nano-0.8"
        assert resolve_model_repo_id("kitten-tts-micro-0.8") == "KittenML/kitten-tts-micro-0.8"

    def test_validate_voice(self):
        backend = KittenTTSBackend()
        assert backend.validate_voice("expr-voice-2-f") is True
        assert backend.validate_voice("expr-voice-5-m") is True
        assert backend.validate_voice("Bella") is True
        assert backend.validate_voice("jasper") is True
        assert backend.validate_voice("nonexistent") is False

    def test_validate_graph_valid(self, simple_graph):
        backend = KittenTTSBackend()
        # Should not raise
        backend.validate_graph(simple_graph)
        backend.validate_graph(None)

    def test_validate_graph_empty_raises(self, empty_graph):
        from cse.acoustic.backend.exceptions import BackendValidationError
        backend = KittenTTSBackend()
        with pytest.raises(BackendValidationError, match="no spoken text"):
            backend.validate_graph(empty_graph)

    def test_translate_mocked(self, tmp_path, fast_graph):
        backend = KittenTTSBackend(KittenTTSConfig(output_dir=tmp_path))
        backend.initialize()

        fake_samples = np.zeros(24000, dtype=np.float32)
        mock_model = MagicMock()
        mock_model.generate.return_value = fake_samples

        backend._ensure_model = MagicMock()
        backend._model = mock_model

        result = backend.translate(fast_graph)

        assert result.success is True
        assert result.backend == "kittentts"
        assert result.sample_rate == 24000
        assert result.audio_path.exists()
        assert result.duration_seconds == 1.0
        assert result.metadata["speed"] == 1.2
        mock_model.generate.assert_called_once_with(
            text="Hurry up!",
            voice="expr-voice-2-f",
            speed=1.2,
        )


# ─── Integration Tests ───────────────────────────────────────────────────────

class TestKittenTTSBackendIntegration:
    def test_full_lifecycle_real_synthesis(self, tmp_path):
        """Perform real synthesis with KittenTTS and verify valid audio file output."""
        backend = KittenTTSBackend(KittenTTSConfig(output_dir=tmp_path))
        backend.initialize()
        backend.load_voice("expr-voice-2-m")

        graph = PerformanceGraph(
            text="Integration test for KittenTTS backend.",
            character_state=None,
            semantics={},
            intent={},
            plan={"delivery": {"pace": "moderate"}},
        )

        result = backend.translate(graph)

        assert result.success is True
        assert result.audio_path.exists()
        assert result.audio_path.stat().st_size > 0
        assert result.duration_seconds > 0.1
        assert result.backend == "kittentts"
        assert result.voice == "expr-voice-2-m"

        backend.shutdown()
        assert backend._initialized is False

    def test_synthesis_with_alias_voice(self, tmp_path):
        """Perform real synthesis using a public alias name (Bella)."""
        backend = KittenTTSBackend(KittenTTSConfig(output_dir=tmp_path))
        backend.initialize()
        backend.load_voice("Bella")

        graph = PerformanceGraph(
            text="Testing public alias voice synthesis.",
            character_state=None,
            semantics={},
            intent={},
            plan={"delivery": {"pace": "fast"}},
        )

        result = backend.translate(graph)

        assert result.success is True
        assert result.audio_path.exists()
        assert result.audio_path.stat().st_size > 0
        assert result.voice == "expr-voice-2-f"

        backend.shutdown()


class TestModelDownload:
    def test_download_all_models_all_succeed(self, tmp_path):
        from cse.backends.kittentts.backend import download_all_models
        import json

        fake_cfg = tmp_path / "config.json"
        fake_cfg.write_text(json.dumps({"voices": "voices.json", "model_file": "model.onnx"}))

        with patch("huggingface_hub.hf_hub_download", return_value=str(fake_cfg)):
            failed = download_all_models()
            assert failed == []

    def test_download_all_models_one_fails(self, tmp_path):
        from cse.backends.kittentts.backend import download_all_models
        import json

        fake_cfg = tmp_path / "config.json"
        fake_cfg.write_text(json.dumps({"voices": "voices.json", "model_file": "model.onnx"}))

        def side_effect(repo_id, filename):
            if "micro" in repo_id:
                raise RuntimeError("Network timeout on micro model")
            return str(fake_cfg)

        with patch("huggingface_hub.hf_hub_download", side_effect=side_effect):
            failed = download_all_models()
            assert len(failed) == 1
            assert failed == ["kitten-tts-micro-0.8"]

    def test_download_all_models_multiple_fail(self):
        from cse.backends.kittentts.backend import download_all_models

        with patch("huggingface_hub.hf_hub_download", side_effect=RuntimeError("Download failed")):
            failed = download_all_models()
            assert len(failed) == 3
            assert "kitten-tts-nano-0.8" in failed
            assert "kitten-tts-micro-0.8" in failed
            assert "kitten-tts-mini-0.8" in failed
