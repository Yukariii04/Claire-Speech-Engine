import pytest
from cse.performance.passes.meaning import MeaningResult
from cse.performance.passes.intent import intent_pass, IntentResult

def test_intent_pass_valid_input():
    meaning = MeaningResult(text="Are we there yet?", character_state=None, semantics={})
    result = intent_pass(meaning)
    
    assert isinstance(result, IntentResult)
    assert result.text == "Are we there yet?"
    # PRD-026: intent dict now includes enriched performance fields
    assert result.intent["primary_intent"] == "question"
    assert result.intent["pace"] == "moderate"
    assert result.intent["pitch_contour"] == "rising"
    assert result.intent["emphasis"] == "final_word"

def test_intent_pass_statements_and_exclamations():
    exclaim = MeaningResult(text="Stop!", character_state=None, semantics={})
    stmt = MeaningResult(text="I am here.", character_state=None, semantics={})
    
    assert intent_pass(exclaim).intent["primary_intent"] == "exclamation"
    assert intent_pass(stmt).intent["primary_intent"] == "statement"

def test_intent_pass_rejects_invalid_input():
    with pytest.raises(TypeError):
        intent_pass("Not a meaning result") # type: ignore

def test_intent_result_immutable():
    result = IntentResult(text="Hi", character_state=None, semantics={}, intent={})
    with pytest.raises(Exception):
        result.intent = {"new": "intent"} # type: ignore
