"""Legacy Performance Compiler (Superseded PRD-003 Baseline).

.. deprecated::
   This module is a legacy PRD-003 baseline retained only for historical
   tests and benchmarks. It is NOT part of the active CPE PerformanceGraph
   speech-generation pipeline and is excluded from built distribution wheels.

Transforms a Claire Intermediate Representation (CIR) into a
deterministic Performance Timeline.

Public API
----------
compile_performance    — Transform a CIRDocument into a PerformanceTimeline.
validate_timeline      — Validate a PerformanceTimeline (raises on error).
serialize_timeline     — Convert a PerformanceTimeline to a JSON string.
deserialize_timeline   — Reconstruct a PerformanceTimeline from a JSON string.
get_version            — Return the Compiler schema version.
"""

from __future__ import annotations

from cse.performance.compiler.compiler import compile_performance
from cse.performance.compiler.serializer import deserialize_timeline, serialize_timeline
from cse.performance.compiler.validator import validate_timeline

from cse.performance.compiler.timeline import COMPILER_VERSION

__all__ = [
    "compile_performance",
    "validate_timeline",
    "serialize_timeline",
    "deserialize_timeline",
    "get_version",
]


def get_version() -> str:
    """Return the Compiler schema version string."""
    return COMPILER_VERSION
