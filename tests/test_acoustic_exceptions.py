"""Tests for acoustic exceptions."""

from __future__ import annotations

from cse.acoustic.backend import (
    BackendError,
    BackendNotFoundError,
    BackendRegistrationError,
    BackendValidationError,
)


class TestAcousticExceptions:
    def test_exception_hierarchy(self):
        assert issubclass(BackendError, Exception)
        assert issubclass(BackendNotFoundError, BackendError)
        assert issubclass(BackendRegistrationError, BackendError)
        assert issubclass(BackendValidationError, BackendError)
