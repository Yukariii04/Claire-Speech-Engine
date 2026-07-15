from abc import ABC, abstractmethod
from typing import Any
from cse.performance.graph import PerformanceGraph

class BaseTranslator(ABC):
    def process(self, graph: Any) -> Any:
        """Process the canonical Performance Graph."""
        if not isinstance(graph, PerformanceGraph):
            raise TypeError("Translator requires a valid PerformanceGraph")
        return self.translate(graph)
        
    @abstractmethod
    def translate(self, graph: PerformanceGraph) -> Any:
        """Produce backend-specific translation output from the Performance Graph."""
        pass
