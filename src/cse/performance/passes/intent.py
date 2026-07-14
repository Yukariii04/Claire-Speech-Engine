from dataclasses import dataclass
from typing import Any
from cse.performance.passes.meaning import MeaningResult

@dataclass(frozen=True)
class IntentResult:
    text: str
    character_state: Any
    semantics: dict
    intent: dict

def intent_pass(result: Any) -> IntentResult:
    """Second reasoning stage: determine communicative intent."""
    if not isinstance(result, MeaningResult):
        raise TypeError("Intent pass requires a valid MeaningResult")
        
    text = result.text.strip()
    
    # Simplest deterministic heuristic for communicative intent
    if text.endswith("?"):
        base_intent = "question"
    elif text.endswith("!"):
        base_intent = "exclamation"
    else:
        base_intent = "statement"
        
    return IntentResult(
        text=result.text,
        character_state=result.character_state,
        semantics=result.semantics,
        intent={"primary_intent": base_intent}
    )
