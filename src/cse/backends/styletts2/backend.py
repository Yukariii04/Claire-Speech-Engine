"""StyleTTS2 AcousticBackend — real inference via styletts2 Python API (PRD-013.6)."""
import uuid as _uuid
from pathlib import Path
from typing import Any

from cse.acoustic.backend.capabilities import BackendCapabilities
from cse.acoustic.backend.interface import AcousticBackend
from cse.backends.kokoro.result import SpeechResult
from cse.backends.kokoro.converter import timeline_to_text
from cse.backends.styletts2.capabilities import get_styletts2_capabilities
from cse.backends.styletts2.exceptions import StyleTTS2InitializationError, SpeechGenerationError


class StyleTTS2Backend(AcousticBackend):
    def __init__(self, config=None):
        self._initialized = False
        self._voice = None
        self._tts = None  # ponytail: lazy-loaded styletts2 engine

    def initialize(self) -> None:
        try:
            import styletts2  # noqa: F401
        except ImportError as e:
            raise StyleTTS2InitializationError(
                "StyleTTS2 not installed. Run: pip install styletts2"
            ) from e
        # ponytail: defer model load to first synthesis call for fast startup
        self._initialized = True

    def shutdown(self) -> None:
        self._initialized = False
        self._tts = None
        self._voice = None

    def _ensure_model(self):
        """Lazy-load the StyleTTS2 model on first use."""
        if self._tts is not None:
            return
        from styletts2 import tts as styletts2_tts
        self._tts = styletts2_tts.StyleTTS2()

    def load_voice(self, voice_name: str) -> str:
        self._voice = voice_name or "default"
        return self._voice

    def synthesize(self, timeline: Any) -> SpeechResult:
        if not self._initialized:
            raise SpeechGenerationError("Backend not initialized.")

        text = timeline_to_text(timeline) if hasattr(timeline, "events") else str(timeline)
        if not text.strip():
            raise SpeechGenerationError("No text to synthesize.")

        self._ensure_model()

        out_path = Path(f"/tmp/styletts2_{_uuid.uuid4().hex[:8]}.wav")

        try:
            # ponytail: styletts2 package provides a simple one-call API
            wav = self._tts.inference(text)

            import soundfile as sf
            sf.write(str(out_path), wav, 24000)

            file_size = out_path.stat().st_size
            duration = max(0.0, (file_size - 44) / (24000 * 2))

            return SpeechResult(
                success=True,
                audio_path=out_path,
                duration_seconds=duration,
                sample_rate=24000,
                channels=1,
                backend="styletts2",
                voice=self._voice or "default",
                metadata={"text": text}
            )
        except Exception as e:
            raise SpeechGenerationError(f"StyleTTS2 inference failed: {e}") from e

    def validate_timeline(self, timeline: Any) -> None:
        pass

    def get_capabilities(self) -> BackendCapabilities:
        return get_styletts2_capabilities()
