from dataclasses import dataclass
from typing import Any, Optional
from cse.performance.passes.meaning import MeaningResult
from cse.performance.passes.explicit_tag_parser import get_explicit_tag_mapping
from cse.performance.passes.deterministic_cues import detect_deterministic_cues

@dataclass(frozen=True)
class IntentResult:
    text: str
    character_state: Any
    semantics: dict
    intent: dict
    explicit_intent_overrides: Optional[str] = None

def intent_pass(result: Any) -> IntentResult:
    """Second reasoning stage: determine communicative intent.

    PRD-026 enrichment:
    - When explicit_intent_overrides is set, use the explicit tag mapping
      and skip deterministic cue detection entirely.
    - When no explicit tag, run deterministic cue detection (punctuation,
      capitalization, lexical) with combination rules.
    - Baseline fallback (? ! .) is preserved within deterministic cues.
    """
    if not isinstance(result, MeaningResult):
        raise TypeError("Intent pass requires a valid MeaningResult")

    if result.explicit_intent_overrides:
        # Explicit tag takes absolute precedence — PRD-026 §6, §9
        # Skip deterministic cue detection entirely
        mapping = get_explicit_tag_mapping(result.explicit_intent_overrides)
        intent = {
            "primary_intent": mapping["primary_intent"],
            "pace": mapping["pace"],
            "pitch_contour": mapping["pitch_contour"],
            "emphasis": mapping["emphasis"],
        }
    else:
        # Deterministic cue detection — PRD-026 §8, §9, §10
        intent = detect_deterministic_cues(result.text)

    return IntentResult(
        text=result.text,
        character_state=result.character_state,
        semantics=result.semantics,
        intent=intent,
        explicit_intent_overrides=result.explicit_intent_overrides,
    )
