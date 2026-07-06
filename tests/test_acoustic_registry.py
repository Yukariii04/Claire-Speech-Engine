"""Tests for Acoustic Backend Registry."""

from __future__ import annotations

import pytest

from cse.acoustic.backend import (
    BackendNotFoundError,
    BackendRegistrationError,
    BackendRegistry,
    DummyBackend,
)


class TestBackendRegistry:
    def test_register_and_get_backend(self):
        registry = BackendRegistry()
        backend = DummyBackend()
        
        registry.register_backend("dummy", backend)
        
        retrieved = registry.get_backend("dummy")
        assert retrieved is backend

    def test_duplicate_registration_raises(self):
        registry = BackendRegistry()
        backend = DummyBackend()
        registry.register_backend("dummy", backend)
        
        with pytest.raises(BackendRegistrationError, match="already registered"):
            registry.register_backend("dummy", backend)

    def test_register_invalid_backend_raises(self):
        registry = BackendRegistry()
        with pytest.raises(BackendRegistrationError, match="must implement AcousticBackend"):
            registry.register_backend("invalid", object())  # type: ignore

    def test_get_unknown_backend_raises(self):
        registry = BackendRegistry()
        with pytest.raises(BackendNotFoundError):
            registry.get_backend("unknown")

    def test_unregister_backend(self):
        registry = BackendRegistry()
        registry.register_backend("dummy", DummyBackend())
        assert "dummy" in registry.list_backends()
        
        registry.unregister_backend("dummy")
        assert "dummy" not in registry.list_backends()
        
        with pytest.raises(BackendNotFoundError):
            registry.get_backend("dummy")

    def test_unregister_unknown_backend_raises(self):
        registry = BackendRegistry()
        with pytest.raises(BackendNotFoundError):
            registry.unregister_backend("unknown")

    def test_list_backends(self):
        registry = BackendRegistry()
        registry.register_backend("a", DummyBackend())
        registry.register_backend("b", DummyBackend())
        
        backends = registry.list_backends()
        assert set(backends) == {"a", "b"}
