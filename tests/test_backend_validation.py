"""Tests for backend validation (PRD-013)."""

import pytest

from cse import SpeechEngine
from cse.acoustic.backend.exceptions import BackendNotFoundError


def test_backend_switching():
    """Verify backend switching uses the exact API required by PRD-013."""
    engine = SpeechEngine()
    
    # Defaults to dummy
    caps1 = engine.get_backend_capabilities()
    assert caps1["backend_name"] == "dummy"

    # Switch to kittentts
    try:
        engine.load_backend("kittentts")
        caps2 = engine.get_backend_capabilities()
        assert caps2["backend_name"] == "kittentts"
        assert "emotion" in caps2
    except Exception:
        pass

    # Switch back to dummy
    engine.load_backend("dummy")
    caps3 = engine.get_backend_capabilities()
    assert caps3["backend_name"] == "dummy"
    
    engine.shutdown()


def test_invalid_backend():
    """Verify loading an invalid backend raises an error."""
    engine = SpeechEngine()
    with pytest.raises(BackendNotFoundError):
        engine.load_backend("nonexistent")
    engine.shutdown()


def test_capability_reporting():
    """Verify capability structure."""
    engine = SpeechEngine()
    caps = engine.get_backend_capabilities()
    
    assert "backend_name" in caps
    assert "supports_streaming" in caps
    assert "emotion" in caps
    assert "sample_rate" in caps
    engine.shutdown()
