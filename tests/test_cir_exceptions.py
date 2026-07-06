"""Tests for CIR exceptions."""

from __future__ import annotations

import pytest

from cse.language.cir.exceptions import (
    CIRBuilderError,
    CIRSerializationError,
    CIRValidationError,
)


class TestCIRExceptions:
    def test_builder_error_is_exception(self):
        assert issubclass(CIRBuilderError, Exception)

    def test_validation_error_is_exception(self):
        assert issubclass(CIRValidationError, Exception)

    def test_serialization_error_is_exception(self):
        assert issubclass(CIRSerializationError, Exception)

    def test_builder_error_message(self):
        with pytest.raises(CIRBuilderError, match="bad input"):
            raise CIRBuilderError("bad input")

    def test_validation_error_message(self):
        with pytest.raises(CIRValidationError, match="missing uuid"):
            raise CIRValidationError("missing uuid")

    def test_serialization_error_message(self):
        with pytest.raises(CIRSerializationError, match="decode fail"):
            raise CIRSerializationError("decode fail")
