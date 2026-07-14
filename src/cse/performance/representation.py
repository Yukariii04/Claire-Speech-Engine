from dataclasses import dataclass
from typing import Any, Optional

@dataclass(frozen=True)
class PerformanceRepresentation:
    text: str
    character_state: Optional[Any] = None

    def __post_init__(self):
        if not self.text:
            raise ValueError("text cannot be empty")
