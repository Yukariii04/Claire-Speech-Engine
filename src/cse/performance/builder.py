from typing import Any
from cse.performance.representation import PerformanceRepresentation

def build_performance_representation(state: Any) -> PerformanceRepresentation:
    """Final pipeline stage: constructs the immutable Performance Representation."""
    text = getattr(state, "text", None)
    character_state = getattr(state, "character_state", None)
    
    if text is None:
        raise ValueError("Invalid state: missing required 'text' field")
        
    return PerformanceRepresentation(text=text, character_state=character_state)
