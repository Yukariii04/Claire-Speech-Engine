import pytest
from cse.performance.translator import BaseTranslator
from cse.performance.representation import PerformanceRepresentation

def test_translator_process_valid():
    class DummyTranslator(BaseTranslator):
        def translate(self, rep: PerformanceRepresentation):
            return "dummy_instructions"
            
    translator = DummyTranslator()
    rep = PerformanceRepresentation(text="Hello")
    assert translator.process(rep) == "dummy_instructions"

def test_translator_rejects_invalid_input():
    class DummyTranslator(BaseTranslator):
        def translate(self, rep: PerformanceRepresentation):
            pass
            
    translator = DummyTranslator()
    with pytest.raises(TypeError):
        translator.process("Not a representation") # type: ignore
