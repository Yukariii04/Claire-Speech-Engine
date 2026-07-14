from typing import Callable, Any
from cse.performance.context import PerformanceContext

class ReasoningPipeline:
    def __init__(self, stages: list[Callable[[Any], Any]]):
        self.stages = stages

    def execute(self, context: PerformanceContext) -> Any:
        if not isinstance(context, PerformanceContext):
            raise TypeError("Input must be a validated PerformanceContext")
        
        state = context
        for stage in self.stages:
            state = stage(state)
            
        return state
