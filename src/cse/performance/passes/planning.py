from dataclasses import dataclass
from typing import Any
from cse.performance.passes.intent import IntentResult

@dataclass(frozen=True)
class PerformancePlan:
    text: str
    character_state: Any
    semantics: dict
    intent: dict
    plan: dict

def planning_pass(result: Any) -> PerformancePlan:
    """Third reasoning stage: determine how speech should be performed."""
    if not isinstance(result, IntentResult):
        raise TypeError("Planning pass requires a valid IntentResult")

    # ponytail: simplest deterministic plan — map intent to delivery style.
    # Upgrade to LLM-driven planning when expressiveness PRDs land.
    intent_type = result.intent.get("primary_intent", "statement")
    delivery = {
        "question": {"pace": "moderate", "pitch_contour": "rising", "emphasis": "final_word"},
        "exclamation": {"pace": "fast", "pitch_contour": "peaked", "emphasis": "throughout"},
        "statement": {"pace": "moderate", "pitch_contour": "flat", "emphasis": "none"},
    }.get(intent_type, {"pace": "moderate", "pitch_contour": "flat", "emphasis": "none"})

    return PerformancePlan(
        text=result.text,
        character_state=result.character_state,
        semantics=result.semantics,
        intent=result.intent,
        plan={"delivery": delivery},
    )
