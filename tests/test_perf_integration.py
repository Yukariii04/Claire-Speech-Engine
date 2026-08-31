import pytest
from cse.performance.context import PerformanceContext
from cse.performance.translator import BaseTranslator
from cse.performance.graph import PerformanceGraph
from cse.performance.integration import execute_end_to_end

class DummyBackendTranslator(BaseTranslator):
    def translate(self, graph: PerformanceGraph) -> dict:
        return {
            "synthesize_text": graph.text,
            "backend_pitch": graph.plan["delivery"]["pitch_contour"]
        }

def test_execute_end_to_end_valid():
    context = PerformanceContext(text="Are we there yet?")
    translator = DummyBackendTranslator()
    
    result = execute_end_to_end(context, translator)
    
    # Verify the entire pipeline ran and correctly passed data
    assert result["synthesize_text"] == "Are we there yet?"
    # Question intent -> rising pitch mapping ensures planning pass ran
    assert result["backend_pitch"] == "rising"

def test_execute_end_to_end_rejects_invalid_context():
    translator = DummyBackendTranslator()
    with pytest.raises(TypeError):
        execute_end_to_end("Not a context", translator) # type: ignore

def test_execute_end_to_end_rejects_invalid_translator():
    context = PerformanceContext(text="Hello.")
    with pytest.raises(AttributeError):
        execute_end_to_end(context, "Not a translator") # type: ignore

def test_generate_performance_graph_from_string():
    from cse.performance.integration import generate_performance_graph
    graph = generate_performance_graph("Hello world.")
    assert isinstance(graph, PerformanceGraph)
    assert graph.text == "Hello world."
    assert graph.intent["primary_intent"] == "statement"

def test_generate_performance_graph_from_context():
    from cse.performance.integration import generate_performance_graph
    context = PerformanceContext(text="[happy] Good morning!")
    graph = generate_performance_graph(context)
    assert isinstance(graph, PerformanceGraph)
    assert graph.text == "Good morning!"
    assert graph.intent["primary_intent"] == "exclamation"

def test_generate_performance_graph_rejects_invalid_type():
    from cse.performance.integration import generate_performance_graph
    with pytest.raises(TypeError):
        generate_performance_graph(12345) # type: ignore
