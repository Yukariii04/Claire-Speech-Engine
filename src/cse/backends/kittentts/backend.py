"""KittenTTS Backend — AcousticBackend implementation.

This is the primary acoustic synthesis backend for the Claire Speech Engine.
All inference is performed via ONNX Runtime through the KittenTTS library.
"""

from __future__ import annotations

import importlib.metadata
import os
import uuid
from pathlib import Path
from typing import Any

from loguru import logger

from cse.acoustic.backend.capabilities import BackendCapabilities
from cse.acoustic.backend.interface import AcousticBackend
from cse.backends.kittentts.config import KittenTTSConfig
from cse.backends.kittentts.exceptions import (
    KittenTTSBackendError,
    KittenTTSInitializationError,
    SpeechGenerationError,
    VoiceLoadError,
)
from cse.backends.kittentts.result import SpeechResult
from cse.performance.graph import PerformanceGraph

# Public voice names mapped to internal expression voice IDs
_VOICE_ALIASES: dict[str, str] = {
    "bella": "expr-voice-2-f",
    "jasper": "expr-voice-2-m",
    "luna": "expr-voice-3-f",
    "bruno": "expr-voice-3-m",
    "rosie": "expr-voice-4-f",
    "hugo": "expr-voice-4-m",
    "kiki": "expr-voice-5-f",
    "leo": "expr-voice-5-m",
}

# Supported KittenTTS voices with friendly metadata
_KITTENTTS_VOICES: list[dict[str, str]] = [
    {"id": "expr-voice-2-f", "name": "Expression 2 Female", "language": "English (US)", "gender": "Female", "alias": "Bella"},
    {"id": "expr-voice-2-m", "name": "Expression 2 Male", "language": "English (US)", "gender": "Male", "alias": "Jasper"},
    {"id": "expr-voice-3-f", "name": "Expression 3 Female", "language": "English (US)", "gender": "Female", "alias": "Luna"},
    {"id": "expr-voice-3-m", "name": "Expression 3 Male", "language": "English (US)", "gender": "Male", "alias": "Bruno"},
    {"id": "expr-voice-4-f", "name": "Expression 4 Female", "language": "English (US)", "gender": "Female", "alias": "Rosie"},
    {"id": "expr-voice-4-m", "name": "Expression 4 Male", "language": "English (US)", "gender": "Male", "alias": "Hugo"},
    {"id": "expr-voice-5-f", "name": "Expression 5 Female", "language": "English (US)", "gender": "Female", "alias": "Kiki"},
    {"id": "expr-voice-5-m", "name": "Expression 5 Male", "language": "English (US)", "gender": "Male", "alias": "Leo"},
]

# Supported KittenTTS models on Hugging Face
_SUPPORTED_MODELS: list[dict[str, Any]] = [
    {
        "id": "kitten-tts-nano-0.8",
        "repo_id": "KittenML/kitten-tts-nano-0.8",
        "name": "Kitten TTS Nano 0.8",
        "size": "~25 MB (15M parameters)",
        "default": True,
    },
    {
        "id": "kitten-tts-micro-0.8",
        "repo_id": "KittenML/kitten-tts-micro-0.8",
        "name": "Kitten TTS Micro 0.8",
        "size": "~45 MB (40M parameters)",
        "default": False,
    },
    {
        "id": "kitten-tts-mini-0.8",
        "repo_id": "KittenML/kitten-tts-mini-0.8",
        "name": "Kitten TTS Mini 0.8",
        "size": "~80 MB (80M parameters)",
        "default": False,
    },
]


def list_models() -> list[dict[str, Any]]:
    """Return the list of supported KittenTTS models."""
    return list(_SUPPORTED_MODELS)


def validate_model(model_id: str) -> bool:
    """Check whether a model ID or repo ID is valid for KittenTTS."""
    if not model_id:
        return False
    mid_clean = model_id.strip()
    return any(m["id"] == mid_clean or m["repo_id"] == mid_clean for m in _SUPPORTED_MODELS)


def resolve_model_repo_id(model_id: str) -> str:
    """Resolve a model ID to its Hugging Face repo ID."""
    mid_clean = model_id.strip()
    for m in _SUPPORTED_MODELS:
        if m["id"] == mid_clean or m["repo_id"] == mid_clean:
            return m["repo_id"]
    return mid_clean


def download_all_models() -> list[str]:
    """Download and cache all supported KittenTTS models.

    Returns:
        list[str]: A list of model IDs that failed to download (empty on full success).
    """
    import json
    from huggingface_hub import hf_hub_download
    failed: list[str] = []
    for m in _SUPPORTED_MODELS:
        repo_id = m["repo_id"]
        logger.info(f"Downloading {m['name']} ({repo_id})...")
        try:
            cfg_path = hf_hub_download(repo_id=repo_id, filename="config.json")
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            if "voices" in cfg:
                hf_hub_download(repo_id=repo_id, filename=cfg["voices"])
            if "model_file" in cfg:
                hf_hub_download(repo_id=repo_id, filename=cfg["model_file"])
        except Exception as e:
            logger.warning(f"Failed to pre-download model {repo_id}: {e}")
            failed.append(m["id"])
    return failed


class KittenTTSBackend(AcousticBackend):
    """Concrete AcousticBackend implementation using KittenTTS (ONNX)."""

    def __init__(self, config: KittenTTSConfig | None = None) -> None:
        self._config = config or KittenTTSConfig()
        self._model = None  # Lazy-loaded KittenTTS instance
        self._loaded_model_name: str | None = None
        self._voice: str | None = None
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the KittenTTS backend.

        Verifies that required dependencies are available without loading
        heavy models or downloading assets immediately.
        """
        try:
            import kittentts  # noqa: F401
        except ImportError as e:
            raise KittenTTSInitializationError(
                "kittentts is not installed. Run: cse setup"
            ) from e
        self._initialized = True

    def _ensure_model(self) -> None:
        """Lazy-load the KittenTTS model on first use."""
        if self._model is not None:
            return

        # Explicitly configure eSpeak if espeakng_loader is present
        try:
            import espeakng_loader
            import phonemizer.backend.espeak.wrapper
            lib_path = espeakng_loader.get_library_path()
            data_path = espeakng_loader.get_data_path()
            phonemizer.backend.espeak.wrapper.EspeakWrapper.set_library(lib_path)
            phonemizer.backend.espeak.wrapper.EspeakWrapper.set_data_path(data_path)
            os.environ["ESPEAK_DATA_PATH"] = data_path
            logger.debug(f"Configured eSpeak via espeakng_loader: lib={lib_path}, data={data_path}")
        except ImportError:
            logger.debug("espeakng_loader is not installed; relying on system eSpeak-NG if available.")
        except Exception as e:
            logger.warning(f"Failed to configure eSpeak via espeakng_loader: {e}")

        try:
            from kittentts import KittenTTS
            from cse.config.user_config import get_preference

            kwargs: dict[str, Any] = {}

            # Determine model: explicit config -> user config preference -> default
            model_target = self._config.model_name
            if model_target == "KittenML/kitten-tts-nano-0.8" or not model_target:
                user_pref = get_preference("model")
                if user_pref:
                    model_target = resolve_model_repo_id(user_pref)

            kwargs["model_name"] = str(model_target)
            if self._config.cache_dir:
                kwargs["cache_dir"] = str(self._config.cache_dir)

            self._model = KittenTTS(**kwargs)
            self._loaded_model_name = str(model_target)
        except Exception as e:
            raise KittenTTSInitializationError(f"Failed to initialize KittenTTS model: {e}") from e

    def shutdown(self) -> None:
        """Shutdown the backend and release resources."""
        self._model = None
        self._loaded_model_name = None
        self._voice = None
        self._initialized = False

    def load_voice(self, voice_name: str | None = None) -> str:
        """Load and validate a KittenTTS voice.

        Args:
            voice_name: Voice identifier (e.g. 'expr-voice-2-f' or alias 'Bella').

        Returns:
            The resolved voice name.
        """
        raw = voice_name or self._config.default_voice
        if not self.validate_voice(raw):
            available = ", ".join(f"{v['id']} ({v['alias']})" for v in self.list_voices())
            raise VoiceLoadError(
                f'Voice "{raw}" is not valid for KittenTTS. Available voices: {available}'
            )
        resolved = _VOICE_ALIASES.get(raw.strip().lower(), raw.strip())
        self._voice = resolved
        return self._voice

    def translate(self, graph: PerformanceGraph) -> SpeechResult:
        """Translate a PerformanceGraph into KittenTTS synthesis parameters and synthesize speech.

        Args:
            graph: A PerformanceGraph instance.

        Returns:
            A SpeechResult containing the path to the generated WAV file.
        """
        if not self._initialized:
            raise SpeechGenerationError("Backend not initialized. Call initialize() first.")

        self._ensure_model()

        if not self._voice:
            self._voice = self._config.default_voice

        text = graph.text
        if not text or not text.strip():
            raise SpeechGenerationError("Graph contains no spoken text.")

        # Map PerformanceGraph fields to KittenTTS parameters
        speed = self._map_speed(graph)
        self._report_unsupported_fields(graph)

        try:
            samples = self._model.generate(
                text=text,
                voice=self._voice,
                speed=speed,
            )
        except Exception as e:
            raise SpeechGenerationError(f"KittenTTS synthesis failed: {e}") from e

        if samples is None or len(samples) == 0:
            raise SpeechGenerationError("KittenTTS produced no audio output.")

        # Save WAV file
        output_dir = Path(self._config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        filename = f"{uuid.uuid4()}.wav"
        output_path = output_dir / filename
        sample_rate = self._config.sample_rate

        try:
            import soundfile as sf
            sf.write(str(output_path), samples, sample_rate)
        except Exception as e:
            raise SpeechGenerationError(f"Failed to save WAV: {e}") from e

        duration_seconds = len(samples) / float(sample_rate)

        return SpeechResult(
            success=True,
            audio_path=output_path,
            duration_seconds=duration_seconds,
            sample_rate=sample_rate,
            channels=1,
            backend="kittentts",
            voice=self._voice,
            metadata={"text": text, "speed": speed, "model": self._loaded_model_name},
        )

    def validate_graph(self, graph: PerformanceGraph) -> None:
        """Validate a PerformanceGraph for the KittenTTS backend."""
        if graph is None:
            return
        if not graph.text or not graph.text.strip():
            from cse.acoustic.backend.exceptions import BackendValidationError
            raise BackendValidationError("Graph contains no spoken text for KittenTTS.")

    def get_capabilities(self) -> BackendCapabilities:
        """Return KittenTTS backend capabilities."""
        pkg_version = "0.8.1"
        try:
            pkg_version = importlib.metadata.version("kittentts")
        except Exception:
            pass

        return BackendCapabilities(
            backend_name="kittentts",
            supports_streaming=False,
            supports_batch=False,
            supports_multispeaker=False,
            supports_voice_cloning=False,
            emotion="limited",
            sample_rate=24000,
            requires_gpu=False,
            supported_languages=("en", "en-us"),
            backend_version=pkg_version,
        )

    def list_voices(self) -> list[dict[str, str]]:
        """Return the list of supported KittenTTS voices."""
        return list(_KITTENTTS_VOICES)

    def validate_voice(self, voice_id: str) -> bool:
        """Check whether a voice ID or alias is valid for KittenTTS."""
        if not voice_id:
            return False
        vid_lower = voice_id.strip().lower()
        if vid_lower in _VOICE_ALIASES:
            return True
        return any(v["id"].lower() == vid_lower for v in _KITTENTTS_VOICES)

    def _map_speed(self, graph: PerformanceGraph) -> float:
        """Extract and map pace from PerformanceGraph to KittenTTS speed factor."""
        plan = graph.plan if isinstance(graph.plan, dict) else {}
        delivery = plan.get("delivery", {})
        pace = delivery.get("pace")

        if pace is None:
            return float(self._config.default_speed)

        if isinstance(pace, (int, float)):
            return float(pace)

        if isinstance(pace, str):
            pace_lower = pace.lower()
            if pace_lower == "fast":
                return 1.2
            elif pace_lower == "slow":
                return 0.8
            elif pace_lower == "moderate":
                return 1.0

        return float(self._config.default_speed)

    def _report_unsupported_fields(self, graph: PerformanceGraph) -> None:
        """Log/report fields that KittenTTS cannot natively represent."""
        unsupported = []
        plan = graph.plan if isinstance(graph.plan, dict) else {}
        delivery = plan.get("delivery", {})

        if "pitch_contour" in delivery and delivery["pitch_contour"] not in (None, "flat"):
            unsupported.append(f"pitch_contour='{delivery['pitch_contour']}'")
        if "emphasis" in delivery and delivery["emphasis"] not in (None, "none"):
            unsupported.append(f"emphasis='{delivery['emphasis']}'")
        if graph.character_state is not None:
            unsupported.append("character_state")

        if unsupported:
            logger.debug(
                f"KittenTTS backend continuing synthesis; unsupported performance fields ignored: {', '.join(unsupported)}"
            )
