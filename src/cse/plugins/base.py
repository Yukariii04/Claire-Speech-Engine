"""Plugin interface — architecture only, no concrete plugins yet."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class PluginBase(ABC):
    """Abstract base for all CSE plugins.

    Every plugin must implement ``initialize``, ``shutdown``, and ``metadata``.
    """

    @abstractmethod
    def initialize(self) -> None:
        """Called once when the plugin is loaded by the runtime."""

    @abstractmethod
    def shutdown(self) -> None:
        """Called once when the runtime is shutting down."""

    @abstractmethod
    def metadata(self) -> dict[str, Any]:
        """Return a dict describing the plugin.

        Expected keys: ``name``, ``version``, ``description``.
        """
