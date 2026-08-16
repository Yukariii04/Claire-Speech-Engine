"""Claire Speech Engine (CSE)."""

__version__ = "1.0.5"

from cse.api.engine import SpeechEngine
from cse.api.config import EngineConfig
from cse.api.exceptions import SpeechEngineError

__all__ = [
    "SpeechEngine",
    "EngineConfig",
    "SpeechEngineError",
    "__version__",
]
