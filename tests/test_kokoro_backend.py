"""Tests for Kokoro Backend (PRD-008 §14).

Tests are split:
  - Unit tests: No model required (converter, loader, config, result, exceptions).
  - Integration tests: Require Kokoro model files (marked with `kokoro_model`).
"""

from __future__ import annotations

import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from cse.backends.kokoro.config import KokoroConfig
from cse.backends.kokoro.converter import timeline_to_text
from cse.backends.kokoro.exceptions import (
    KokoroBackendError,
    KokoroInitializationError,
    SpeechGenerationError,
    VoiceLoadError,
)
from cse.backends.kokoro.loader import resolve_voice
from cse.backends.kokoro.result import SpeechResult
from cse.performance.compiler.events import EVENT_TOKEN, EVENT_PAUSE, PerformanceEvent
from cse.performance.compiler.timeline import PerformanceTimeline, PerformanceMetadata


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def simple_timeline():
    """A timeline with spoken text tokens."""
    events = (
        PerformanceEvent(
            uuid=uuid.uuid4(),
            timestamp_ms=0,
            event_type=EVENT_TOKEN,
            parameters={"token": "Hello"},
        ),
        PerformanceEvent(
            uuid=uuid.uuid4(),
            timestamp_ms=100,
            event_type=EVENT_PAUSE,
            parameters={"duration_ms": 200},
        ),
        PerformanceEvent(
            uuid=uuid.uuid4(),
            timestamp_ms=300,
            event_type=EVENT_TOKEN,
            parameters={"token": "world"},
        ),
    )
    return PerformanceTimeline(
        uuid=uuid.uuid4(),
        version="1.0.0",
        events=events,
        metadata=PerformanceMetadata(),
    )


@pytest.fixture
def empty_timeline():
    """A timeline with no spoken text."""
    return PerformanceTimeline(
        uuid=uuid.uuid4(),
        version="1.0.0",
        events=(),
        metadata=PerformanceMetadata(),
    )


# ─── Exception Tests ─────────────────────────────────────────────────────────

class TestExceptions:
    def test_exception_hierarchy(self):
        assert issubclass(KokoroBackendError, Exception)
        assert issubclass(KokoroInitializationError, KokoroBackendError)
        assert issubclass(VoiceLoadError, KokoroBackendError)
        assert issubclass(SpeechGenerationError, KokoroBackendError)


# ─── Config Tests ─────────────────────────────────────────────────────────────

class TestKokoroConfig:
    def test_default_config(self):
        config = KokoroConfig()
        assert config.lang_code == "en-us"
        assert config.sample_rate == 24000
        assert config.default_voice == "af_heart"

    def test_custom_config(self):
        config = KokoroConfig(default_voice="af_sarah", output_dir="output")
        assert config.default_voice == "af_sarah"
        assert config.output_dir == "output"


# ─── Converter Tests ──────────────────────────────────────────────────────────

class TestConverter:
    def test_extracts_only_tokens(self, simple_timeline):
        text = timeline_to_text(simple_timeline)
        assert text == "Hello world"

    def test_empty_timeline(self, empty_timeline):
        text = timeline_to_text(empty_timeline)
        assert text == ""


# ─── Loader Tests ─────────────────────────────────────────────────────────────

class TestLoader:
    def test_resolve_voice(self):
        assert resolve_voice("af_sarah", "af_heart") == "af_sarah"

    def test_resolve_voice_default(self):
        assert resolve_voice(None, "af_heart") == "af_heart"

    def test_resolve_voice_empty_raises(self):
        with pytest.raises(VoiceLoadError):
            resolve_voice("", "")


# ─── SpeechResult Tests ──────────────────────────────────────────────────────

class TestSpeechResult:
    def test_immutable(self):
        result = SpeechResult(
            success=True,
            audio_path=Path("/tmp/test.wav"),
            duration_seconds=1.5,
            sample_rate=24000,
            channels=1,
            backend="kokoro",
            voice="af_heart",
        )
        assert result.success is True
        assert result.backend == "kokoro"

        # Frozen
        with pytest.raises(AttributeError):
            result.success = False  # type: ignore


# ─── Backend Unit Tests (Mocked) ─────────────────────────────────────────────

class TestKokoroBackendUnit:
    def test_initialize_missing_import(self):
        from cse.backends.kokoro.backend import KokoroBackend

        backend = KokoroBackend()
        with patch.dict("sys.modules", {"kokoro_onnx": None}):
            with pytest.raises(KokoroInitializationError):
                backend.initialize()

    def test_synthesize_without_init(self, simple_timeline):
        from cse.backends.kokoro.backend import KokoroBackend

        backend = KokoroBackend()
        with pytest.raises(SpeechGenerationError, match="not initialized"):
            backend.synthesize(simple_timeline)

    def test_synthesize_empty_text(self, empty_timeline):
        from cse.backends.kokoro.backend import KokoroBackend

        backend = KokoroBackend()
        backend._initialized = True
        backend._kokoro = MagicMock()
        backend._voice = "af_heart"

        with pytest.raises(SpeechGenerationError, match="no spoken text"):
            backend.synthesize(empty_timeline)

    def test_shutdown(self):
        from cse.backends.kokoro.backend import KokoroBackend

        backend = KokoroBackend()
        backend._initialized = True
        backend._kokoro = MagicMock()

        backend.shutdown()

        assert backend._initialized is False
        assert backend._kokoro is None

    def test_load_voice(self):
        from cse.backends.kokoro.backend import KokoroBackend

        backend = KokoroBackend()
        resolved = backend.load_voice("af_sarah")
        assert resolved == "af_sarah"

    def test_get_capabilities(self):
        from cse.backends.kokoro.backend import KokoroBackend

        backend = KokoroBackend()
        caps = backend.get_capabilities()
        assert caps.supports_batch is True
        assert caps.requires_gpu is False
        assert "en" in caps.supported_languages

    def test_validate_timeline_empty(self, empty_timeline):
        from cse.backends.kokoro.backend import KokoroBackend
        from cse.acoustic.backend.exceptions import BackendValidationError

        backend = KokoroBackend()
        with pytest.raises(BackendValidationError):
            backend.validate_timeline(empty_timeline)

    def test_validate_timeline_none(self):
        from cse.backends.kokoro.backend import KokoroBackend

        backend = KokoroBackend()
        backend.validate_timeline(None)  # Should not raise

    def test_synthesize_mocked(self, simple_timeline, tmp_path):
        """Full synthesis flow with mocked Kokoro."""
        from cse.backends.kokoro.backend import KokoroBackend

        config = KokoroConfig(output_dir=str(tmp_path))
        backend = KokoroBackend(config=config)
        backend._initialized = True
        backend._voice = "af_heart"

        # Mock the Kokoro instance
        mock_kokoro = MagicMock()
        fake_audio = np.zeros(24000, dtype=np.float32)  # 1 second of silence
        mock_kokoro.create.return_value = (fake_audio, 24000)
        backend._kokoro = mock_kokoro

        result = backend.synthesize(simple_timeline)

        assert result.success is True
        assert result.audio_path.exists()
        assert result.audio_path.suffix == ".wav"
        assert result.duration_seconds == pytest.approx(1.0)
        assert result.sample_rate == 24000
        assert result.backend == "kokoro"
        assert result.voice == "af_heart"
        assert result.metadata["text"] == "Hello world"


# ─── Integration Tests (require model) ───────────────────────────────────────

MODEL_PATH = Path("models/kokoro/kokoro-v1.0.onnx")
VOICES_PATH = Path("models/kokoro/voices-v1.0.bin")

kokoro_model = pytest.mark.skipif(
    not (MODEL_PATH.exists() and VOICES_PATH.exists()),
    reason="Kokoro model files not found. Download from GitHub releases.",
)


@kokoro_model
class TestKokoroBackendIntegration:
    def test_full_lifecycle(self, simple_timeline, tmp_path):
        from cse.backends.kokoro.backend import KokoroBackend

        config = KokoroConfig(
            output_dir=str(tmp_path),
            model_path=MODEL_PATH,
            voices_path=VOICES_PATH,
        )
        backend = KokoroBackend(config=config)

        # Initialize
        backend.initialize()
        assert backend._initialized is True

        # Load voice
        voice = backend.load_voice("af_heart")
        assert voice == "af_heart"

        # Synthesize
        result = backend.synthesize(simple_timeline)
        assert result.success is True
        assert result.audio_path.exists()
        assert result.duration_seconds > 0
        assert result.sample_rate == 24000

        # Shutdown
        backend.shutdown()
        assert backend._initialized is False
