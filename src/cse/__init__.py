"""The Claire Speech Engine (CSE)."""

__version__ = "1.0.4"

from .api import SpeechEngine
from .api.exceptions import SpeechEngineError

__all__ = ["SpeechEngine", "__version__"]
