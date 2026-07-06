"""Tests for Dummy Backend (refactored)."""

from __future__ import annotations

import pytest

from cse.acoustic.backend import DummyBackend


class TestDummyBackend:
    def test_dummy_backend_raises_not_implemented(self):
        backend = DummyBackend()
        backend.initialize()
        
        with pytest.raises(NotImplementedError, match="Dummy backend does not synthesize"):
            backend.synthesize(None)
            
        backend.shutdown()

    def test_dummy_backend_capabilities(self):
        backend = DummyBackend()
        caps = backend.get_capabilities()
        
        assert caps.supports_streaming is False
        assert caps.supports_batch is False
        assert caps.supports_multispeaker is False
        assert caps.supports_voice_cloning is False
        assert caps.requires_gpu is False
        assert "en" in caps.supported_languages
        assert caps.backend_version == "1.0.0"

    def test_validate_timeline(self):
        backend = DummyBackend()
        # dummy backend doesn't raise anything
        backend.validate_timeline(None)
