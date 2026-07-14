import pytest
from cse.performance.context import PerformanceContext

def test_performance_context_valid():
    ctx = PerformanceContext(text="Hello", character_state={"mood": "happy"})
    assert ctx.text == "Hello"
    assert ctx.character_state == {"mood": "happy"}

def test_performance_context_empty_text():
    with pytest.raises(ValueError):
        PerformanceContext(text="")

def test_performance_context_optional_state():
    ctx = PerformanceContext(text="No state")
    assert ctx.character_state is None

def test_performance_context_immutable():
    ctx = PerformanceContext(text="Hello")
    with pytest.raises(Exception): # dataclass FrozenInstanceError
        ctx.text = "New"
