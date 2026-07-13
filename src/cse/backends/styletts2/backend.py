"""StyleTTS2 AcousticBackend — real inference via styletts2 Python API (PRD-013.6)."""
import logging
import threading
import uuid as _uuid
from pathlib import Path
from typing import Any

from cse.acoustic.backend.capabilities import BackendCapabilities
from cse.acoustic.backend.interface import AcousticBackend
from cse.backends.kokoro.result import SpeechResult
from cse.backends.kokoro.converter import timeline_to_text
from cse.backends.styletts2.capabilities import get_styletts2_capabilities
from cse.backends.styletts2.exceptions import StyleTTS2InitializationError, SpeechGenerationError

# ponytail: reuse the same bundled asset from fishspeech
_BUNDLED_ASSET = Path(__file__).parent.parent / "fishspeech" / "assets" / "claire_neutral.wav"

_log = logging.getLogger(__name__)

# ponytail: module-level lock so two concurrent first-loads can't race on torch.load patch.
# Accepted limitation: while held, any other code calling torch.load also sees weights_only=False,
# since torch.load is process-global and styletts2 doesn't expose the flag.
_model_lock = threading.Lock()


class StyleTTS2Backend(AcousticBackend):
    def __init__(self, config=None):
        self._initialized = False
        self._voice = None
        self._ref_path = None  # ponytail: resolved reference wav path
        self._tts = None

    def initialize(self) -> None:
        try:
            import styletts2  # noqa: F401
            # ponytail: nltk recently split 'punkt' into 'punkt_tab', which styletts2
            # doesn't auto-download. Force download on init to prevent inference crashes.
            import nltk
            nltk.download('punkt', quiet=True)
            nltk.download('punkt_tab', quiet=True)
        except ImportError as e:
            raise StyleTTS2InitializationError(
                "StyleTTS2 not installed. Run: pip install styletts2"
            ) from e
        # ponytail: defer model load to first synthesis call per RELEASE-002 §1a
        self._initialized = True

    def shutdown(self) -> None:
        self._initialized = False
        self._tts = None
        self._voice = None
        self._ref_path = None

    def _ensure_model(self):
        """Lazy-load the StyleTTS2 model on first use, thread-safe."""
        if self._tts is not None:
            return
        with _model_lock:
            # Double-check after acquiring lock
            if self._tts is not None:
                return
            # ponytail: StyleTTS2 checkpoints use pickle globals incompatible with
            # PyTorch 2.6+ weights_only=True default. Patch for the load call only.
            import torch
            _original_load = torch.load
            torch.load = lambda *a, **kw: _original_load(*a, **{**kw, "weights_only": False})
            try:
                from styletts2 import tts as styletts2_tts
                self._tts = styletts2_tts.StyleTTS2()
            finally:
                torch.load = _original_load

    def load_voice(self, voice_name: str) -> str:
        self._voice = voice_name or "claire_neutral"
        # ponytail: accept an explicit path or fall back to bundled default
        candidate = Path(voice_name) if voice_name else _BUNDLED_ASSET
        if candidate.exists() and candidate.suffix == ".wav":
            self._ref_path = candidate
        else:
            self._ref_path = _BUNDLED_ASSET
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
                voice=self._voice or "claire_neutral",
                metadata={"text": text}
            )
        except Exception as e:
            raise SpeechGenerationError(f"StyleTTS2 inference failed: {e}") from e

    def validate_timeline(self, timeline: Any) -> None:
        pass

    def get_capabilities(self) -> BackendCapabilities:
        return get_styletts2_capabilities()

    def list_voices(self) -> list[dict[str, str]]:
        """StyleTTS2 ships with the bundled claire_neutral reference voice."""
        # ponytail: styletts2 package doesn't expose multi-voice; one entry
        return [{"id": "claire_neutral", "name": "Claire Neutral", "language": "English", "gender": "Female"}]

