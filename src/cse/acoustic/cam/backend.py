"""CAM-001 Native Acoustic Backend (PRD-028 §2, §4, §5, §8, §26).

Concrete AcousticBackend implementation for the native Claire Acoustic Model (CAM).
Executes two-stage ONNX Runtime inference:
    PerformanceGraph
        ↓
    GraphToConditioningAdapter
        ↓
    cam_acoustic.onnx
        ↓
    cam_vocoder.onnx
        ↓
    24 kHz Audio (WAV)
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import onnxruntime as ort
import soundfile as sf
from loguru import logger

from cse.acoustic.backend.capabilities import BackendCapabilities
from cse.acoustic.backend.exceptions import (
    BackendError,
    BackendValidationError,
)
from cse.acoustic.cam.exceptions import (
    CAMBackendError,
    CAMInitializationError,
    SpeechGenerationError,
    VoiceLoadError,
)
from cse.acoustic.backend.interface import AcousticBackend
from cse.acoustic.cam.adapter import GraphToConditioningAdapter
from cse.acoustic.cam.config import (
    CAMConfig,
    EXPRESSO_READ_STYLES,
    EXPRESSO_SPEAKERS,
    ID_TO_STYLE,
    STYLE_TO_ID,
)
from cse.acoustic.cam.downloader import resolve_cam_model_paths
from cse.backends.kittentts.result import SpeechResult
from cse.performance.graph import PerformanceGraph


# Build catalog of native CAM voices across Expresso speakers and 8 read styles
_CAM_VOICES: list[dict[str, str]] = []
for spk in EXPRESSO_SPEAKERS:
    for style in EXPRESSO_READ_STYLES:
        voice_id = f"cam-{spk}-{style}"
        _CAM_VOICES.append({
            "id": voice_id,
            "name": f"CAM {spk.replace('_', ' ').title()} ({style.title()})",
            "language": "English (US)",
            "gender": "Female" if "0" in spk or "2" in spk else "Male",
            "speaker": spk,
            "style": style,
        })


class CAMBackend(AcousticBackend):
    """Concrete AcousticBackend implementation for native CAM (ONNX)."""

    def __init__(self, config: CAMConfig | None = None, quantized: bool = True) -> None:
        self.config = config or CAMConfig()
        self.quantized = quantized
        self.adapter = GraphToConditioningAdapter(self.config)

        self._acoustic_session: ort.InferenceSession | None = None
        self._vocoder_session: ort.InferenceSession | None = None
        self._active_voice: str = "cam-speaker_0-default"
        self._active_speaker: str = "speaker_0"
        self._active_style: str = "default"
        self._initialized: bool = False

    def initialize(self) -> None:
        """Initialize the CAM backend without loading heavy models immediately."""
        self._initialized = True

    def _ensure_sessions(self) -> None:
        """Lazy-load ONNX Runtime inference sessions on first synthesis."""
        if self._acoustic_session is not None and self._vocoder_session is not None:
            return

        acoustic_path, vocoder_path = resolve_cam_model_paths(
            acoustic_path=self.config.acoustic_model_path,
            vocoder_path=self.config.vocoder_model_path,
            quantized=self.quantized,
        )

        session_opts = ort.SessionOptions()
        session_opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

        # Try CUDA if available, fallback to CPU
        providers = ["CPUExecutionProvider"]
        if "CUDAExecutionProvider" in ort.get_available_providers():
            providers.insert(0, "CUDAExecutionProvider")

        logger.info(f"Loading CAM Acoustic ONNX: {acoustic_path} with providers {providers}")
        self._acoustic_session = ort.InferenceSession(str(acoustic_path), session_opts, providers=providers)

        logger.info(f"Loading CAM Vocoder ONNX: {vocoder_path} with providers {providers}")
        self._vocoder_session = ort.InferenceSession(str(vocoder_path), session_opts, providers=providers)

    def shutdown(self) -> None:
        """Release ONNX Runtime inference sessions and resources."""
        self._acoustic_session = None
        self._vocoder_session = None
        self._initialized = False

    def list_voices(self) -> list[dict[str, str]]:
        """Return structured metadata for all native CAM voices."""
        return list(_CAM_VOICES)

    def validate_voice(self, voice_id: str) -> bool:
        """Check whether a voice ID is valid for CAM."""
        if not voice_id:
            return False
        vid = voice_id.strip().lower()
        # Accept either exact cam ID or bare style name or speaker
        if any(v["id"] == vid for v in _CAM_VOICES):
            return True
        if vid in EXPRESSO_READ_STYLES or vid in EXPRESSO_SPEAKERS:
            return True
        return False

    def load_voice(self, voice_name: str | None = None) -> str:
        """Load and configure an active CAM voice."""
        raw = voice_name or "cam-speaker_0-default"
        raw_clean = raw.strip().lower()

        if not self.validate_voice(raw_clean):
            available = ", ".join(v["id"] for v in _CAM_VOICES[:8]) + "..."
            raise VoiceLoadError(
                f'Voice "{raw}" is not valid for CAM. Available voices: {available}'
            )

        # Parse speaker and style from voice identifier
        for v in _CAM_VOICES:
            if v["id"] == raw_clean:
                self._active_voice = v["id"]
                self._active_speaker = v["speaker"]
                self._active_style = v["style"]
                return self._active_voice

        if raw_clean in EXPRESSO_READ_STYLES:
            self._active_style = raw_clean
            self._active_voice = f"cam-{self._active_speaker}-{self._active_style}"
        elif raw_clean in EXPRESSO_SPEAKERS:
            self._active_speaker = raw_clean
            self._active_voice = f"cam-{self._active_speaker}-{self._active_style}"
        else:
            self._active_voice = raw_clean

        return self._active_voice

    def validate_graph(self, graph: PerformanceGraph) -> None:
        """Validate a PerformanceGraph for CAM synthesis."""
        if graph is None:
            return
        if not graph.text or not graph.text.strip():
            raise BackendValidationError("PerformanceGraph contains no spoken text for CAM.")

    def translate(self, graph: PerformanceGraph) -> SpeechResult:
        """Translate a PerformanceGraph into synthesized 24 kHz audio via ONNX Runtime."""
        if not self._initialized:
            raise SpeechGenerationError("CAMBackend is not initialized. Call initialize() first.")

        self.validate_graph(graph)
        self._ensure_sessions()

        # 1. Adapt PerformanceGraph to CAM conditioning tensors
        cond = self.adapter.adapt(
            graph,
            speaker=self._active_speaker,
            style_override=self._active_style,
        )

        # 2. Run Stage 1: cam_acoustic.onnx
        acoustic_feed = {
            "phoneme_ids": cond.phoneme_ids,
            "speaker_id": cond.speaker_id,
            "style_id": cond.style_id,
            "intent_id": cond.intent_id,
            "pace": cond.pace,
            "pitch_contour_id": cond.pitch_contour_id,
            "emphasis_id": cond.emphasis_id,
        }

        try:
            acoustic_out = self._acoustic_session.run(None, acoustic_feed)
            mel_output = acoustic_out[0]  # [1, T_frames, 80]
        except Exception as e:
            raise SpeechGenerationError(f"CAM acoustic ONNX inference failed: {e}") from e

        # 3. Run Stage 2: cam_vocoder.onnx
        try:
            vocoder_out = self._vocoder_session.run(None, {"mel": mel_output})
            waveform = vocoder_out[0]  # [1, 1, T_samples]
        except Exception as e:
            raise SpeechGenerationError(f"CAM vocoder ONNX inference failed: {e}") from e

        # Flatten waveform array
        audio_samples = waveform.squeeze()
        if audio_samples.ndim > 1:
            audio_samples = audio_samples.flatten()

        # 4. Save 24 kHz WAV output
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{uuid.uuid4()}.wav"
        output_path = output_dir / filename
        sample_rate = self.config.sample_rate  # Strictly 24000 Hz

        try:
            sf.write(str(output_path), audio_samples, sample_rate)
        except Exception as e:
            raise SpeechGenerationError(f"Failed to write audio output WAV: {e}") from e

        duration_sec = len(audio_samples) / float(sample_rate)

        return SpeechResult(
            success=True,
            audio_path=output_path,
            duration_seconds=duration_sec,
            sample_rate=sample_rate,
            channels=1,
            backend="cam",
            voice=self._active_voice,
            metadata={
                "text": graph.text,
                "speaker": self._active_speaker,
                "style": self._active_style,
                "sample_rate": sample_rate,
            },
        )

    def get_capabilities(self) -> BackendCapabilities:
        """Return native CAM backend capabilities."""
        return BackendCapabilities(
            backend_name="cam",
            supports_streaming=False,
            supports_batch=True,
            supports_multispeaker=True,
            supports_voice_cloning=False,
            emotion="high",
            sample_rate=self.config.sample_rate,  # 24000
            requires_gpu=False,
            supported_languages=("en", "en-us"),
            backend_version="1.0.0",
        )
