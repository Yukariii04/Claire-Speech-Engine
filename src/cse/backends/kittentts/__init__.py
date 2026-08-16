"""KittenTTS Backend for Claire Speech Engine."""

from cse.backends.kittentts.backend import KittenTTSBackend
from cse.backends.kittentts.config import KittenTTSConfig
from cse.backends.kittentts.exceptions import (
    KittenTTSBackendError,
    KittenTTSInitializationError,
    SpeechGenerationError,
    VoiceLoadError,
)
from cse.backends.kittentts.result import SpeechResult

__all__ = [
    "KittenTTSBackend",
    "KittenTTSConfig",
    "SpeechResult",
    "KittenTTSBackendError",
    "KittenTTSInitializationError",
    "VoiceLoadError",
    "SpeechGenerationError",
]
