import pytest
from cse.performance.passes.planning import PerformancePlan
from cse.performance.graph import build_performance_graph, PerformanceGraph

def _make_plan(**overrides):
    defaults = dict(text="Hello.", character_state=None, semantics={"raw_meaning": "Hello."}, intent={"primary_intent": "statement"}, plan={"delivery": {"pace": "moderate"}})
    defaults.update(overrides)
    return PerformancePlan(**defaults)

def test_build_graph_valid():
    plan = _make_plan()
    graph = build_performance_graph(plan)

    assert isinstance(graph, PerformanceGraph)
    assert graph.text == "Hello."
    assert graph.plan == {"delivery": {"pace": "moderate"}}

def test_build_graph_preserves_all_fields():
    plan = _make_plan(character_state={"mood": "calm"}, semantics={"raw_meaning": "Hi"}, intent={"primary_intent": "exclamation"})
    graph = build_performance_graph(plan)

    assert graph.character_state == {"mood": "calm"}
    assert graph.semantics == {"raw_meaning": "Hi"}
    assert graph.intent == {"primary_intent": "exclamation"}

def test_build_graph_rejects_invalid_input():
    with pytest.raises(TypeError):
        build_performance_graph("not a plan")  # type: ignore

def test_performance_graph_immutable():
    graph = PerformanceGraph(text="Hi", character_state=None, semantics={}, intent={}, plan={})
    with pytest.raises(Exception):
        graph.text = "Bye"  # type: ignore

def test_build_graph_does_not_modify_plan():
    plan = _make_plan()
    build_performance_graph(plan)
    # Plan should still be intact (frozen, so this is guaranteed, but verify)
    assert plan.text == "Hello."
    assert plan.plan == {"delivery": {"pace": "moderate"}}
