import pytest
from cse.performance.representation import PerformanceRepresentation
from cse.performance.builder import build_performance_representation
from dataclasses import dataclass

def test_performance_representation_valid():
    rep = PerformanceRepresentation(text="Hello", character_state={"mood": "happy"})
    assert rep.text == "Hello"
    assert rep.character_state == {"mood": "happy"}

def test_performance_representation_immutable():
    rep = PerformanceRepresentation(text="Hello")
    with pytest.raises(Exception):
        rep.text = "New" # type: ignore

def test_builder_creates_representation():
    @dataclass
    class MockState:
        text: str
        character_state: dict = None # type: ignore

    state = MockState(text="Build me", character_state={"status": "ready"})
    rep = build_performance_representation(state)
    
    assert isinstance(rep, PerformanceRepresentation)
    assert rep.text == "Build me"
    assert rep.character_state == {"status": "ready"}

def test_builder_rejects_invalid_state():
    class InvalidState:
        pass
        
    with pytest.raises(ValueError):
        build_performance_representation(InvalidState())
