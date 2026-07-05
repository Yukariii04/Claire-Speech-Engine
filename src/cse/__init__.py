"""Claire Speech Engine (CSE).

Production-grade speech synthesis foundation.
"""

__version__ = "0.1.0"

from cse.config.manager import get_config
from cse.core.logger import get_logger
from cse.core.registry import get_registry
from cse.runtime.bootstrap import bootstrap, shutdown

__all__ = [
    "bootstrap",
    "shutdown",
    "get_config",
    "get_logger",
    "get_registry",
]
