"""Performance Compiler — compiles CIR into a Performance Timeline."""

from __future__ import annotations

import uuid
from typing import Any

from cse.language.cir.schema import CIRDocument
from cse.performance.compiler.events import (
    EVENT_SPEAK_END,
    EVENT_SPEAK_START,
    EVENT_TOKEN,
    PerformanceEvent,
)
from cse.performance.compiler.exceptions import PerformanceCompilerError
from cse.performance.compiler.timeline import PerformanceMetadata, PerformanceTimeline, COMPILER_VERSION

# PRD §13 - Performance attributes initialized to 0.5
_DEFAULT_ATTRIBUTES = {
    "warmth": 0.5,
    "energy": 0.5,
    "confidence": 0.5,
    "affection": 0.5,
    "curiosity": 0.5,
    "playfulness": 0.5,
    "breathiness": 0.5,
    "tension": 0.5,
    "dominance": 0.5,
    "excitement": 0.5,
}

# UUID namespace for performance compiler
_PERF_NAMESPACE = uuid.UUID("f4a1b2c3-d4e5-f678-90ab-cdef12345678")


def _generate_event_id(seed: str) -> uuid.UUID:
    """Deterministic UUID generation for events."""
    return uuid.uuid5(_PERF_NAMESPACE, seed)


def compile_performance(cir_document: CIRDocument) -> PerformanceTimeline:
    """Compile a CIRDocument into a deterministic PerformanceTimeline.

    Args:
        cir_document: The parsed CIR document.

    Returns:
        A PerformanceTimeline.
    """
    if not cir_document or not hasattr(cir_document, "utterances"):
        raise PerformanceCompilerError("Invalid CIRDocument provided.")

    events: list[PerformanceEvent] = []
    current_time_ms = 0

    for u_idx, utt in enumerate(cir_document.utterances):
        for s_idx, seg in enumerate(utt.segments):
            # PRD §12: Generate Speak Start
            start_id = _generate_event_id(f"start:{u_idx}:{s_idx}:{current_time_ms}")
            events.append(
                PerformanceEvent(
                    uuid=start_id,
                    timestamp_ms=current_time_ms,
                    event_type=EVENT_SPEAK_START,
                    parameters={},
                )
            )

            # Generate Tokens
            for t_idx, token in enumerate(seg.tokens):
                params: dict[str, Any] = {
                    "token": token.text,
                    "segment_index": s_idx,
                    "token_index": t_idx,
                }
                params.update(_DEFAULT_ATTRIBUTES)

                tok_id = _generate_event_id(
                    f"tok:{u_idx}:{s_idx}:{t_idx}:{current_time_ms}:{token.text}"
                )
                events.append(
                    PerformanceEvent(
                        uuid=tok_id,
                        timestamp_ms=current_time_ms,
                        event_type=EVENT_TOKEN,
                        parameters=params,
                    )
                )

                # PRD §14: 150 ms per token
                current_time_ms += 150

            # Generate Speak End
            end_id = _generate_event_id(f"end:{u_idx}:{s_idx}:{current_time_ms}")
            events.append(
                PerformanceEvent(
                    uuid=end_id,
                    timestamp_ms=current_time_ms,
                    event_type=EVENT_SPEAK_END,
                    parameters={},
                )
            )
            # Add a minor gap between segments/utterances if needed, but PRD doesn't mention it.
            # Keeping it strictly 150ms per token as per example.

    tl_id = _generate_event_id(f"timeline:{cir_document.uuid}")
    return PerformanceTimeline(
        uuid=tl_id,
        version=COMPILER_VERSION,
        events=tuple(events),
        metadata=PerformanceMetadata(cir_uuid=str(cir_document.uuid)),
    )
