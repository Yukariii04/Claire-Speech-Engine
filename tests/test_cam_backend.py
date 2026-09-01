"""Tests for CAM Backend and Engine Integration (PRD-028 §2, §4, §5, §25, §26)."""

import os
from pathlib import Path
import pytest
import soundfile as sf

from cse.acoustic.cam.backend import CAMBackend
from cse.acoustic.cam.config import CAMConfig, EXPRESSO_READ_STYLES, EXPRESSO_SPEAKERS
from cse.api.engine import SpeechEngine
from cse.backends.kittentts.result import SpeechResult
from cse.performance.graph import PerformanceGraph
from cse.runtime.voice.runtime import VoiceRuntime


@pytest.fixture
def cam_backend(tmp_path):
    cfg = CAMConfig(output_dir=tmp_path / "cam_out")
    backend = CAMBackend(config=cfg, quantized=True)
    backend.initialize()
    yield backend
    backend.shutdown()


class TestCAMBackend:
    def test_initialization_and_capabilities(self, cam_backend):
        caps = cam_backend.get_capabilities()
        assert caps.backend_name == "cam"
        assert caps.sample_rate == 24000
        assert caps.emotion == "high"
        assert caps.supports_batch is True
        assert caps.supports_multispeaker is True

    def test_list_voices_contains_expresso_read_set(self, cam_backend):
        voices = cam_backend.list_voices()
        assert len(voices) == len(EXPRESSO_SPEAKERS) * len(EXPRESSO_READ_STYLES)
        for v in voices:
            assert v["style"] in EXPRESSO_READ_STYLES
            assert v["speaker"] in EXPRESSO_SPEAKERS

    def test_load_voice(self, cam_backend):
        assert cam_backend.validate_voice("cam-speaker_0-happy") is True
        loaded = cam_backend.load_voice("cam-speaker_0-happy")
        assert loaded == "cam-speaker_0-happy"
        assert cam_backend._active_speaker == "speaker_0"
        assert cam_backend._active_style == "happy"

    def test_translate_generates_24khz_audio(self, cam_backend):
        graph = PerformanceGraph(
            text="Claire Acoustic Model is synthesizing twenty-four kilohertz speech.",
            character_state={"style": "narration"},
            semantics={"text": "Claire Acoustic Model is synthesizing twenty-four kilohertz speech."},
            intent={"primary_intent": "statement", "pace": "moderate", "pitch_contour": "flat", "emphasis": "none"},
            plan={"delivery": {"pace": "moderate", "pitch_contour": "flat", "emphasis": "none"}},
        )

        res = cam_backend.translate(graph)
        assert isinstance(res, SpeechResult)
        assert res.success is True
        assert res.sample_rate == 24000
        assert res.audio_path.exists()

        # Verify WAV file sample rate with soundfile
        info = sf.info(str(res.audio_path))
        assert info.samplerate == 24000
        assert info.channels == 1
        assert info.duration > 0.1

    def test_voice_runtime_load_cam_backend(self, tmp_path):
        runtime = VoiceRuntime()
        runtime.initialize()
        runtime.load_backend("cam")
        assert runtime.get_backend_id() == "cam"
        assert isinstance(runtime.get_backend(), CAMBackend)

        runtime.load_voice("cam-speaker_0-default")
        graph = PerformanceGraph(
            text="Testing runtime integration.",
            character_state=None,
            semantics={},
            intent={"primary_intent": "statement"},
            plan={"delivery": {"pace": "moderate", "pitch_contour": "flat", "emphasis": "none"}},
        )
        res = runtime.process(graph)
        assert isinstance(res, SpeechResult)
        assert res.sample_rate == 24000
        runtime.shutdown()

    def test_speech_engine_cam_integration(self, tmp_path):
        engine = SpeechEngine()
        engine.load_backend("cam")
        assert engine.get_backend_capabilities()["backend_name"] == "cam"
        assert engine.get_backend_capabilities()["sample_rate"] == 24000

        engine.load_voice("cam-speaker_0-happy")
        res = engine.speak("The speech engine successfully speaks using the native Claire Acoustic Model!")
        assert isinstance(res, SpeechResult)
        assert res.sample_rate == 24000
        assert res.audio_path.exists()
        engine.shutdown()
