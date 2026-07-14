import pytest
from cse.performance.context import PerformanceContext
from cse.performance.pipeline import ReasoningPipeline

def test_pipeline_sequential_execution():
    def stage1(state):
        return state + " -> stage1"
        
    def stage2(state):
        return state + " -> stage2"

    pipeline = ReasoningPipeline([stage1, stage2])
    ctx = PerformanceContext(text="init")
    
    # We bypass the type checker for the state purely for this simple mock test
    # but the first stage normally receives the PerformanceContext itself.
    def extract_text(ctx):
        return ctx.text
        
    pipeline = ReasoningPipeline([extract_text, stage1, stage2])
    result = pipeline.execute(ctx)
    
    assert result == "init -> stage1 -> stage2"

def test_pipeline_rejects_invalid_input():
    pipeline = ReasoningPipeline([])
    with pytest.raises(TypeError):
        pipeline.execute("Not A Performance Context") # type: ignore
