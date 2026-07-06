"""UUID generation for CIR objects.

Requirements (PRD §13):
- Deterministic within one build (seeded from raw_text).
- Globally unique across builds (UUID5 with a CIR namespace).
- Serializable (standard UUID string representation).
"""

from __future__ import annotations

import uuid

# Fixed namespace UUID for all CIR identifiers.
CIR_NAMESPACE = uuid.UUID("a1b2c3d4-e5f6-7890-abcd-ef1234567890")


def generate_id(seed: str) -> uuid.UUID:
    """Return a deterministic UUID5 for *seed* within the CIR namespace."""
    return uuid.uuid5(CIR_NAMESPACE, seed)
