"""Golden tests for the performance compiler (PRD §22)."""

from __future__ import annotations

import json
import pytest

from cse.language.cir import build_cir
from cse.performance.compiler import compile_performance, serialize_timeline


def test_golden_hello():
    """Matches the golden example in PRD-003 §22 and §25."""
    cir = build_cir("Hello.")
    tl = compile_performance(cir)
    
    # We will verify the exact structure matches the PRD example
    tl_dict = json.loads(serialize_timeline(tl))
    
    events = tl_dict["events"]
    assert len(events) == 3
    
    assert events[0]["event_type"] == "SPEAK_START"
    assert events[0]["timestamp_ms"] == 0
    
    assert events[1]["event_type"] == "TOKEN"
    assert events[1]["timestamp_ms"] == 0
    assert events[1]["parameters"]["token"] == "Hello"
    assert events[1]["parameters"]["warmth"] == 0.5
    
    assert events[2]["event_type"] == "SPEAK_END"
    assert events[2]["timestamp_ms"] == 150
