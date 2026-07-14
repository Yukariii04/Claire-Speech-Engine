from dataclasses import dataclass
from typing import Any, Optional
from cse.performance.context import PerformanceContext

@dataclass(frozen=True)
class MeaningResult:
    text: str
    character_state: Optional[Any]
    semantics: dict

def meaning_pass(context: Any) -> MeaningResult:
    """First reasoning stage: determine semantic meaning of the text."""
    if not isinstance(context, PerformanceContext):
        raise TypeError("Meaning pass requires a valid PerformanceContext")
        
    # In ponytail mode, the simplest deterministic semantic analysis
    # is capturing the raw string as the semantic payload.
    return MeaningResult(
        text=context.text,
        character_state=context.character_state,
        semantics={"raw_meaning": context.text}
    )
