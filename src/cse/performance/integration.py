from typing import Any, Union
from cse.performance.context import PerformanceContext
from cse.performance.pipeline import ReasoningPipeline
from cse.performance.translator import BaseTranslator
from cse.performance.passes.meaning import meaning_pass
from cse.performance.passes.intent import intent_pass
from cse.performance.passes.planning import planning_pass
from cse.performance.passes.explicit_tag_parser import parse_explicit_tag
from cse.performance.graph import build_performance_graph, PerformanceGraph


def generate_performance_graph(input_data: Union[PerformanceContext, str]) -> PerformanceGraph:
    """Canonical CPE reasoning pipeline.

    Processes a PerformanceContext or raw text string through the full CPE
    reasoning stages to produce a canonical backend-independent PerformanceGraph.

    Pipeline stages:
        PerformanceContext
            ↓
        Explicit Tag Parsing
            ↓
        Meaning Pass
            ↓
        Intent Pass
            ↓
        Planning Pass
            ↓
        Performance Graph Builder

    Returns:
        The canonical immutable PerformanceGraph.
    """
    if isinstance(input_data, str):
        context = PerformanceContext(text=input_data)
    elif isinstance(input_data, PerformanceContext):
        context = input_data
    else:
        raise TypeError("Input must be a validated PerformanceContext or text string")

    # PRD-026: Explicit tag parsing happens before the pipeline stages.
    # If a valid tag is present, it is stripped from text and stored in
    # explicit_intent_overrides. If no tag, text passes through unchanged.
    tag, cleaned_text = parse_explicit_tag(context.text)
    if tag is not None:
        context = PerformanceContext(
            text=cleaned_text,
            character_state=context.character_state,
            explicit_intent_overrides=tag,
        )

    pipeline = ReasoningPipeline([
        meaning_pass,
        intent_pass,
        planning_pass,
        build_performance_graph,
    ])

    return pipeline.execute(context)


def execute_end_to_end(context: PerformanceContext, translator: BaseTranslator) -> Any:
    """Execute the CPE pipeline from context to translated backend instructions.

    Uses the canonical generate_performance_graph pipeline and translates the
    resulting PerformanceGraph into backend-specific instructions.
    """
    if not isinstance(context, PerformanceContext):
        raise TypeError("Input must be a validated PerformanceContext")

    graph = generate_performance_graph(context)
    return translator.process(graph)
