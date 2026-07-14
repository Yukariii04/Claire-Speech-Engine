import pytest
from cse.performance.context import PerformanceContext
from cse.performance.passes.meaning import meaning_pass, MeaningResult

def test_meaning_pass_valid_input():
    ctx = PerformanceContext(text="Hello world", character_state={"mood": "happy"})
    result = meaning_pass(ctx)
    
    assert isinstance(result, MeaningResult)
    assert result.text == "Hello world"
    assert result.character_state == {"mood": "happy"}
    # Character state ignored for semantics, deterministic output based on text
    assert result.semantics == {"raw_meaning": "Hello world"}

def test_meaning_pass_rejects_invalid_input():
    with pytest.raises(TypeError):
        meaning_pass("Just a string") # type: ignore

def test_meaning_result_immutable():
    result = MeaningResult(text="Hi", character_state=None, semantics={})
    with pytest.raises(Exception):
        result.text = "New" # type: ignore
