"""Performance Timeline — immutable root object (PRD §8)."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from cse.performance.compiler.events import PerformanceEvent

# Version matches PRD-003 version
COMPILER_VERSION = "1.0.0"


@dataclass(frozen=True)
class PerformanceMetadata:
    """Metadata for the timeline."""

    source: str = "compiler"
    cir_uuid: str = ""


@dataclass(frozen=True)
class PerformanceTimeline:
    """Root object of a compiled performance."""

    uuid: UUID
    version: str
    events: tuple[PerformanceEvent, ...]
    metadata: PerformanceMetadata = field(default_factory=PerformanceMetadata)
