"""The Claire Speech Engine (CSE)."""

__version__ = "1.0.0-beta"

from .api import SpeechEngine
from .api.exceptions import SpeechEngineError

__all__ = ["SpeechEngine", "__version__"]
