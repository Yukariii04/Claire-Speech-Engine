"""Timeline Converter (PRD-008 §9).

Converts a PerformanceTimeline into plain text for the Kokoro backend.
Per PRD-008: ignore emphasis, pauses, and breathing — only extract spoken text.
"""

from __future__ import annotations

from typing import Any

from cse.performance.compiler.events import EVENT_TOKEN


def timeline_to_text(timeline: Any) -> str:
    """Extract spoken text from a PerformanceTimeline.

    Only TOKEN events are processed. All expressive features
    (emphasis, pauses, breathing) are deliberately ignored
    per PRD-008 §9.
    """
    tokens: list[str] = []

    for event in timeline.events:
        if event.event_type == EVENT_TOKEN:
            # Token text is under the 'token' key in the parameters
            text = event.parameters.get("token", "")
            if text:
                tokens.append(text)

    return " ".join(tokens)
