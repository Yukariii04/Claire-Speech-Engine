"""Tests for voice backend."""

from __future__ import annotations

import pytest

from cse.runtime.voice.backend import DummyBackend


class TestDummyBackend:
    def test_dummy_backend_raises_not_implemented(self):
        backend = DummyBackend()
        backend.initialize()
        
        with pytest.raises(NotImplementedError, match="Dummy backend does not synthesize"):
            backend.synthesize(None)
            
        backend.shutdown()

    def test_dummy_backend_streaming(self):
        backend = DummyBackend()
        assert backend.supports_streaming() is False
