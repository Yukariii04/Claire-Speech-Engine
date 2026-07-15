import pytest
from cse.performance.passes.intent import IntentResult
from cse.performance.passes.planning import planning_pass, PerformancePlan

def test_planning_pass_question():
    intent = IntentResult(text="Are we there yet?", character_state=None, semantics={}, intent={"primary_intent": "question"})
    result = planning_pass(intent)

    assert isinstance(result, PerformancePlan)
    assert result.text == "Are we there yet?"
    assert result.plan["delivery"]["pitch_contour"] == "rising"

def test_planning_pass_exclamation():
    intent = IntentResult(text="Stop!", character_state=None, semantics={}, intent={"primary_intent": "exclamation"})
    result = planning_pass(intent)

    assert result.plan["delivery"]["pace"] == "fast"
    assert result.plan["delivery"]["emphasis"] == "throughout"

def test_planning_pass_statement():
    intent = IntentResult(text="Hello.", character_state=None, semantics={}, intent={"primary_intent": "statement"})
    result = planning_pass(intent)

    assert result.plan["delivery"]["pitch_contour"] == "flat"

def test_planning_pass_rejects_invalid_input():
    with pytest.raises(TypeError):
        planning_pass("Not an IntentResult")  # type: ignore

def test_performance_plan_immutable():
    plan = PerformancePlan(text="Hi", character_state=None, semantics={}, intent={}, plan={})
    with pytest.raises(Exception):
        plan.plan = {"new": "plan"}  # type: ignore

def test_planning_pass_preserves_fields():
    intent = IntentResult(text="Okay", character_state={"mood": "calm"}, semantics={"raw_meaning": "Okay"}, intent={"primary_intent": "statement"})
    result = planning_pass(intent)

    assert result.character_state == {"mood": "calm"}
    assert result.semantics == {"raw_meaning": "Okay"}
    assert result.intent == {"primary_intent": "statement"}
