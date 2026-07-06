"""Tests for voice runtime exceptions."""

from __future__ import annotations

import pytest

from cse.runtime.voice.exceptions import (
    BackendNotRegisteredError,
    InvalidRuntimeStateError,
    VoiceNotFoundError,
    VoiceRuntimeError,
)


class TestVoiceExceptions:
    def test_base_error_is_exception(self):
        assert issubclass(VoiceRuntimeError, Exception)

    def test_voice_not_found_is_runtime_error(self):
        assert issubclass(VoiceNotFoundError, VoiceRuntimeError)

    def test_backend_not_registered_is_runtime_error(self):
        assert issubclass(BackendNotRegisteredError, VoiceRuntimeError)

    def test_invalid_state_is_runtime_error(self):
        assert issubclass(InvalidRuntimeStateError, VoiceRuntimeError)
