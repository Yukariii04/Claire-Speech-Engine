from dataclasses import dataclass
from typing import Any, Optional
from cse.performance.passes.intent import IntentResult

@dataclass(frozen=True)
class PerformancePlan:
    text: str
    character_state: Any
    semantics: dict
    intent: dict
    plan: dict
    explicit_intent_overrides: Optional[str] = None

def planning_pass(result: Any) -> PerformancePlan:
    """Third reasoning stage: determine how speech should be performed.

    PRD-026: The intent dict now carries full enriched performance data
    (primary_intent, pace, pitch_contour, emphasis) from either explicit
    tag mappings or deterministic cue detection. The planning pass uses
    these directly as the delivery plan.
    """
    if not isinstance(result, IntentResult):
        raise TypeError("Planning pass requires a valid IntentResult")

    # PRD-026: intent dict already contains the full enriched mapping
    # (primary_intent, pace, pitch_contour, emphasis) from either:
    #   - explicit tag mapping, or
    #   - deterministic cue detection, or
    #   - baseline fallback
    intent = result.intent
    delivery = {
        "pace": intent.get("pace", "moderate"),
        "pitch_contour": intent.get("pitch_contour", "flat"),
        "emphasis": intent.get("emphasis", "none"),
    }

    return PerformancePlan(
        text=result.text,
        character_state=result.character_state,
        semantics=result.semantics,
        intent=result.intent,
        plan={"delivery": delivery},
        explicit_intent_overrides=result.explicit_intent_overrides,
    )
