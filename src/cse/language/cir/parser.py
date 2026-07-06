"""CIR Parser — entry point for text → CIR conversion (PRD §18).

The parser is intentionally thin: it delegates to the builder.
Supported input: English UTF-8.
"""

from __future__ import annotations

from cse.language.cir.builder import build_cir
from cse.language.cir.schema import CIRDocument

__all__ = ["parse"]


def parse(text: str) -> CIRDocument:
    """Parse raw English UTF-8 text into a ``CIRDocument``.

    This is an alias for ``build_cir`` provided for semantic clarity.

    Args:
        text: Raw text input.

    Returns:
        A CIRDocument.
    """
    return build_cir(text)
