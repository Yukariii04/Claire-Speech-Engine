from abc import ABC, abstractmethod
from typing import Any
from cse.performance.representation import PerformanceRepresentation

class BaseTranslator(ABC):
    def process(self, representation: Any) -> Any:
        if not isinstance(representation, PerformanceRepresentation):
            raise TypeError("Translator requires a valid PerformanceRepresentation")
        return self.translate(representation)
        
    @abstractmethod
    def translate(self, representation: PerformanceRepresentation) -> Any:
        pass
