"""Backend Registry (PRD-005 §8)."""

from __future__ import annotations

import threading

from cse.acoustic.backend.exceptions import BackendNotFoundError, BackendRegistrationError
from cse.acoustic.backend.interface import AcousticBackend


class BackendRegistry:
    """Thread-safe registry for acoustic backends."""

    def __init__(self) -> None:
        self._backends: dict[str, AcousticBackend] = {}
        self._lock = threading.RLock()

    def register_backend(self, backend_id: str, backend: AcousticBackend) -> None:
        """Register a backend instance."""
        if not isinstance(backend, AcousticBackend):
            raise BackendRegistrationError("Backend must implement AcousticBackend interface.")
            
        with self._lock:
            if backend_id in self._backends:
                raise BackendRegistrationError(f"Backend '{backend_id}' is already registered.")
            self._backends[backend_id] = backend

    def unregister_backend(self, backend_id: str) -> None:
        """Unregister a backend."""
        with self._lock:
            if backend_id not in self._backends:
                raise BackendNotFoundError(f"Backend '{backend_id}' not found.")
            del self._backends[backend_id]

    def get_backend(self, backend_id: str) -> AcousticBackend:
        """Get a backend by ID."""
        with self._lock:
            if backend_id not in self._backends:
                raise BackendNotFoundError(f"Backend '{backend_id}' not found.")
            return self._backends[backend_id]

    def list_backends(self) -> list[str]:
        """List all registered backend IDs."""
        with self._lock:
            return list(self._backends.keys())
