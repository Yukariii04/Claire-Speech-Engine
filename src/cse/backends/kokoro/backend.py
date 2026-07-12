"""Kokoro Backend — AcousticBackend implementation (PRD-008 §5).

This is the ONLY module in CSE that imports Kokoro-specific libraries.
The rest of CSE remains completely unaware that Kokoro exists.

Uses `kokoro-onnx` for Python 3.13+ compatibility (avoids numpy==1.26.4 pin
from the official `kokoro` package).
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

import numpy as np

from cse.acoustic.backend.capabilities import BackendCapabilities
from cse.acoustic.backend.interface import AcousticBackend
from cse.backends.kokoro.config import KokoroConfig
from cse.backends.kokoro.converter import timeline_to_text
from cse.backends.kokoro.exceptions import (
    KokoroInitializationError,
    SpeechGenerationError,
    VoiceLoadError,
)
from cse.backends.kokoro.loader import resolve_voice
from cse.backends.kokoro.result import SpeechResult


class KokoroBackend(AcousticBackend):
    """Concrete AcousticBackend implementation using Kokoro TTS (ONNX)."""

    def __init__(self, config: KokoroConfig | None = None) -> None:
        self._config = config or KokoroConfig()
        self._kokoro = None  # Lazy-loaded Kokoro instance
        self._voice: str | None = None
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the Kokoro ONNX pipeline."""
        try:
            from kokoro_onnx import Kokoro  # Only import here

            model_path = str(self._config.model_path)
            voices_path = str(self._config.voices_path)

            if not Path(model_path).exists():
                raise KokoroInitializationError(
                    f"Model file not found: {model_path}. "
                    "Download from: https://github.com/thewh1teagle/kokoro-onnx/releases"
                )
            if not Path(voices_path).exists():
                raise KokoroInitializationError(
                    f"Voices file not found: {voices_path}. "
                    "Download from: https://github.com/thewh1teagle/kokoro-onnx/releases"
                )

            self._kokoro = Kokoro(model_path, voices_path)
            self._initialized = True
        except ImportError as e:
            raise KokoroInitializationError(
                "kokoro-onnx is not installed. Run: pip install kokoro-onnx soundfile"
            ) from e
        except KokoroInitializationError:
            raise
        except Exception as e:
            raise KokoroInitializationError(f"Failed to initialize Kokoro: {e}") from e

    def shutdown(self) -> None:
        """Shutdown the Kokoro pipeline."""
        self._kokoro = None
        self._voice = None
        self._initialized = False

    def load_voice(self, voice_name: str | None = None) -> str:
        """Load a Kokoro voice.

        Args:
            voice_name: Kokoro voice identifier (e.g. 'af_sarah', 'af_heart').

        Returns:
            The resolved voice name.
        """
        self._voice = resolve_voice(voice_name, self._config.default_voice)
        return self._voice

    def synthesize(self, timeline: Any) -> SpeechResult:
        """Synthesize speech from a PerformanceTimeline.

        Args:
            timeline: A PerformanceTimeline instance.

        Returns:
            A SpeechResult containing the path to the generated WAV file.
        """
        if not self._initialized or not self._kokoro:
            raise SpeechGenerationError("Backend not initialized. Call initialize() first.")

        if not self._voice:
            self._voice = self._config.default_voice

        # PRD-008 §9: Convert timeline to plain text
        text = timeline_to_text(timeline)
        if not text.strip():
            raise SpeechGenerationError("Timeline contains no spoken text.")

        # Generate audio using kokoro-onnx
        try:
            samples, sample_rate = self._kokoro.create(
                text,
                voice=self._voice,
                speed=1.0,
                lang=self._config.lang_code,
            )
        except Exception as e:
            raise SpeechGenerationError(f"Kokoro synthesis failed: {e}") from e

        if samples is None or len(samples) == 0:
            raise SpeechGenerationError("Kokoro produced no audio output.")

        # Save WAV file
        output_dir = Path(self._config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{uuid.uuid4()}.wav"
        output_path = output_dir / filename

        try:
            import soundfile as sf

            sf.write(str(output_path), samples, sample_rate)
        except Exception as e:
            raise SpeechGenerationError(f"Failed to save WAV: {e}") from e

        duration_seconds = len(samples) / sample_rate

        return SpeechResult(
            success=True,
            audio_path=output_path,
            duration_seconds=duration_seconds,
            sample_rate=sample_rate,
            channels=1,
            backend="kokoro",
            voice=self._voice,
            metadata={"text": text},
        )

    def validate_timeline(self, timeline: Any) -> None:
        """Validate a timeline for the Kokoro backend."""
        if timeline is None:
            return
        text = timeline_to_text(timeline)
        if not text.strip():
            from cse.acoustic.backend.exceptions import BackendValidationError

            raise BackendValidationError("Timeline contains no spoken text for Kokoro.")

    def get_capabilities(self) -> BackendCapabilities:
        """Return Kokoro backend capabilities."""
        return BackendCapabilities(
            backend_name="kokoro",
            supports_streaming=False,
            supports_batch=True,
            supports_multispeaker=True,
            supports_voice_cloning=False,
            emotion="limited",
            sample_rate=24000,
            requires_gpu=False,
            supported_languages=("en",),
            backend_version="1.0.0",
        )

    def list_voices(self) -> list[dict[str, str]]:
        """Return all Kokoro voices with structured metadata."""
        return [
            {"id": "af_alloy", "name": "Alloy", "language": "English (US)", "gender": "Female"},
            {"id": "af_aoede", "name": "Aoede", "language": "English (US)", "gender": "Female"},
            {"id": "af_bella", "name": "Bella", "language": "English (US)", "gender": "Female"},
            {"id": "af_heart", "name": "Heart", "language": "English (US)", "gender": "Female"},
            {"id": "af_jessica", "name": "Jessica", "language": "English (US)", "gender": "Female"},
            {"id": "af_kore", "name": "Kore", "language": "English (US)", "gender": "Female"},
            {"id": "af_nicole", "name": "Nicole", "language": "English (US)", "gender": "Female"},
            {"id": "af_nova", "name": "Nova", "language": "English (US)", "gender": "Female"},
            {"id": "af_river", "name": "River", "language": "English (US)", "gender": "Female"},
            {"id": "af_sarah", "name": "Sarah", "language": "English (US)", "gender": "Female"},
            {"id": "af_sky", "name": "Sky", "language": "English (US)", "gender": "Female"},
            {"id": "am_adam", "name": "Adam", "language": "English (US)", "gender": "Male"},
            {"id": "am_echo", "name": "Echo", "language": "English (US)", "gender": "Male"},
            {"id": "am_eric", "name": "Eric", "language": "English (US)", "gender": "Male"},
            {"id": "am_fable", "name": "Fable", "language": "English (US)", "gender": "Male"},
            {"id": "am_liam", "name": "Liam", "language": "English (US)", "gender": "Male"},
            {"id": "am_michael", "name": "Michael", "language": "English (US)", "gender": "Male"},
            {"id": "am_onyx", "name": "Onyx", "language": "English (US)", "gender": "Male"},
            {"id": "am_puck", "name": "Puck", "language": "English (US)", "gender": "Male"},
            {"id": "am_santa", "name": "Santa", "language": "English (US)", "gender": "Male"},
            {"id": "bf_alice", "name": "Alice", "language": "English (GB)", "gender": "Female"},
            {"id": "bf_emma", "name": "Emma", "language": "English (GB)", "gender": "Female"},
            {"id": "bf_isabella", "name": "Isabella", "language": "English (GB)", "gender": "Female"},
            {"id": "bf_lily", "name": "Lily", "language": "English (GB)", "gender": "Female"},
            {"id": "bm_daniel", "name": "Daniel", "language": "English (GB)", "gender": "Male"},
            {"id": "bm_fable", "name": "Fable (GB)", "language": "English (GB)", "gender": "Male"},
            {"id": "bm_george", "name": "George", "language": "English (GB)", "gender": "Male"},
            {"id": "bm_lewis", "name": "Lewis", "language": "English (GB)", "gender": "Male"},
        ]

