"""Tests for Acoustic Backend Manager."""

from __future__ import annotations
from unittest.mock import MagicMock

import pytest

from cse.acoustic.backend import (
    BackendManager,
    BackendNotFoundError,
    BackendRegistry,
    BackendValidationError,
    DummyBackend,
)


class TestBackendManager:
    def test_manager_selects_backend(self):
        registry = BackendRegistry()
        dummy = DummyBackend()
        registry.register_backend("dummy", dummy)
        
        manager = BackendManager(registry)
        assert manager.backend is None
        
        manager.select("dummy")
        assert manager.backend is dummy

    def test_manager_initialize_and_shutdown(self):
        registry = BackendRegistry()
        # Use a mock backend to verify calls
        backend = MagicMock(spec=DummyBackend)
        registry.register_backend("mock", backend)
        
        manager = BackendManager(registry)
        manager.select("mock")
        
        manager.initialize()
        backend.initialize.assert_called_once()
        assert manager._initialized is True
        
        manager.shutdown()
        backend.shutdown.assert_called_once()
        assert manager._initialized is False

    def test_initialize_without_selection_raises(self):
        registry = BackendRegistry()
        manager = BackendManager(registry)
        with pytest.raises(BackendNotFoundError, match="No active backend selected"):
            manager.initialize()

    def test_select_while_initialized_shuts_down_previous(self):
        registry = BackendRegistry()
        b1 = MagicMock(spec=DummyBackend)
        b2 = MagicMock(spec=DummyBackend)
        registry.register_backend("b1", b1)
        registry.register_backend("b2", b2)
        
        manager = BackendManager(registry)
        manager.select("b1")
        manager.initialize()
        
        # Select b2
        manager.select("b2")
        
        # Verify b1 was shut down and manager is no longer initialized
        b1.shutdown.assert_called_once()
        assert manager._initialized is False
        assert manager.backend is b2

    def test_validate_before_synthesis(self):
        registry = BackendRegistry()
        dummy = DummyBackend()
        registry.register_backend("dummy", dummy)
        
        manager = BackendManager(registry)
        manager.select("dummy")
        
        # Not initialized yet
        with pytest.raises(BackendValidationError, match="Backend is not initialized"):
            manager.validate_before_synthesis(None)
            
        manager.initialize()
        manager.validate_before_synthesis(None)  # Should pass
