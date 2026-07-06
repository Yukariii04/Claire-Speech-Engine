"""Tests for performance compiler exceptions."""

from __future__ import annotations

import pytest

from cse.performance.compiler.exceptions import (
    PerformanceCompilerError,
    TimelineSerializationError,
    TimelineValidationError,
)


class TestPerformanceExceptions:
    def test_compiler_error_is_exception(self):
        assert issubclass(PerformanceCompilerError, Exception)

    def test_validation_error_is_exception(self):
        assert issubclass(TimelineValidationError, Exception)

    def test_serialization_error_is_exception(self):
        assert issubclass(TimelineSerializationError, Exception)

    def test_compiler_error_message(self):
        with pytest.raises(PerformanceCompilerError, match="bad"):
            raise PerformanceCompilerError("bad")
