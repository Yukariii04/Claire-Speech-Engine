"""Claire Intermediate Representation (CIR).

The canonical immutable internal representation of all language
entering Claire Speech Engine.  Every downstream system MUST
consume CIR instead of raw text.

Public API
----------
build_cir      — Parse raw text into a CIRDocument.
validate       — Validate a CIRDocument (raises on error).
serialize      — Convert a CIRDocument to a JSON string.
deserialize    — Reconstruct a CIRDocument from a JSON string.
get_version    — Return the CIR schema version.
"""

from __future__ import annotations

from cse.language.cir.builder import build_cir
from cse.language.cir.serializer import deserialize, serialize
from cse.language.cir.validator import validate
from cse.language.cir.schema import CIR_VERSION

__all__ = [
    "build_cir",
    "validate",
    "serialize",
    "deserialize",
    "get_version",
]


def get_version() -> str:
    """Return the CIR schema version string."""
    return CIR_VERSION
