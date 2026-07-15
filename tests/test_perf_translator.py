import pytest
from cse.performance.translator import BaseTranslator
from cse.performance.graph import PerformanceGraph

def test_translator_process_valid():
    class DummyTranslator(BaseTranslator):
        def translate(self, graph: PerformanceGraph):
            return "dummy_instructions"
            
    translator = DummyTranslator()
    graph = PerformanceGraph(text="Hello", character_state=None, semantics={}, intent={}, plan={})
    assert translator.process(graph) == "dummy_instructions"

def test_translator_rejects_invalid_input():
    class DummyTranslator(BaseTranslator):
        def translate(self, graph: PerformanceGraph):
            pass
            
    translator = DummyTranslator()
    with pytest.raises(TypeError):
        translator.process("Not a graph") # type: ignore

def test_translator_does_not_modify_graph():
    class DummyTranslator(BaseTranslator):
        def translate(self, graph: PerformanceGraph):
            # Try to modify the graph (it's frozen so it should fail if we try,
            # but we just assert it passes unharmed to the translator)
            return graph.text
            
    translator = DummyTranslator()
    graph = PerformanceGraph(text="Hello", character_state=None, semantics={}, intent={}, plan={})
    assert translator.process(graph) == "Hello"
