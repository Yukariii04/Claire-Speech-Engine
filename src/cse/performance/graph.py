from dataclasses import dataclass
from typing import Any
from cse.performance.passes.planning import PerformancePlan

@dataclass(frozen=True)
class PerformanceGraph:
    """Canonical backend-independent representation consumed by translators."""
    text: str
    character_state: Any
    semantics: dict
    intent: dict
    plan: dict

def build_performance_graph(result: Any) -> PerformanceGraph:
    """Build the immutable Performance Graph from a completed Performance Plan."""
    if not isinstance(result, PerformancePlan):
        raise TypeError("Performance Graph Builder requires a valid PerformancePlan")

    # ponytail: graph is a sealed snapshot of all reasoning outputs.
    # Add structured graph fields (nodes/edges) when translators need them.
    return PerformanceGraph(
        text=result.text,
        character_state=result.character_state,
        semantics=result.semantics,
        intent=result.intent,
        plan=result.plan,
    )
