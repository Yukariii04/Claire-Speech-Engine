from typing import Any
from cse.performance.context import PerformanceContext
from cse.performance.pipeline import ReasoningPipeline
from cse.performance.translator import BaseTranslator
from cse.performance.passes.meaning import meaning_pass
from cse.performance.passes.intent import intent_pass
from cse.performance.passes.planning import planning_pass
from cse.performance.graph import build_performance_graph

def execute_end_to_end(context: PerformanceContext, translator: BaseTranslator) -> Any:
    """Execute the complete Phase 1 pipeline from context to translated backend instructions."""
    pipeline = ReasoningPipeline([
        meaning_pass,
        intent_pass,
        planning_pass,
        build_performance_graph,
    ])
    
    # Run the reasoning pipeline to get the canonical graph
    graph = pipeline.execute(context)
    
    # Translate the graph into backend-specific instructions
    return translator.process(graph)
