"""Backend Manager (PRD-005 §9)."""

from __future__ import annotations
from typing import Any

from cse.acoustic.backend.exceptions import BackendError, BackendNotFoundError
from cse.acoustic.backend.interface import AcousticBackend
from cse.acoustic.backend.registry import BackendRegistry
from cse.acoustic.backend.validator import validate_backend_state


class BackendManager:
    """Manages the active backend."""

    def __init__(self, registry: BackendRegistry) -> None:
        self._registry = registry
        self._active_backend: AcousticBackend | None = None
        self._initialized = False

    @property
    def backend(self) -> AcousticBackend | None:
        """Expose the current active backend."""
        return self._active_backend

    def select(self, backend_id: str) -> None:
        """Select an active backend from the registry."""
        if self._initialized and self._active_backend:
            self.shutdown()
            
        self._active_backend = self._registry.get_backend(backend_id)
        self._initialized = False

    def initialize(self) -> None:
        """Initialize the active backend."""
        if not self._active_backend:
            raise BackendNotFoundError("No active backend selected.")
        self._active_backend.initialize()
        self._initialized = True

    def shutdown(self) -> None:
        """Shutdown the active backend."""
        if self._active_backend and self._initialized:
            self._active_backend.shutdown()
            self._initialized = False

    def validate_before_synthesis(self, graph: Any) -> None:
        """Validate state before synthesis."""
        validate_backend_state(
            backend_initialized=self._initialized,
            backend_active=self._active_backend is not None
        )
        if self._active_backend:
            self._active_backend.validate_graph(graph)
