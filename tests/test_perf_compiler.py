"""Tests for the performance compiler (PRD §12-14, §21)."""

from __future__ import annotations

import pytest

from cse.language.cir import build_cir
from cse.performance.compiler import compile_performance
from cse.performance.compiler.events import (
    EVENT_SPEAK_END,
    EVENT_SPEAK_START,
    EVENT_TOKEN,
)
from cse.performance.compiler.exceptions import PerformanceCompilerError
from cse.performance.compiler.timeline import PerformanceTimeline


class TestCompilePerformance:
    def test_returns_timeline(self):
        cir = build_cir("Hello.")
        tl = compile_performance(cir)
        assert isinstance(tl, PerformanceTimeline)

    def test_simple_sentence_events(self):
        cir = build_cir("Hello.")
        tl = compile_performance(cir)
        
        # Expected: START -> TOKEN -> END
        assert len(tl.events) == 3
        assert tl.events[0].event_type == EVENT_SPEAK_START
        assert tl.events[1].event_type == EVENT_TOKEN
        assert tl.events[2].event_type == EVENT_SPEAK_END

    def test_timestamps_deterministic(self):
        cir = build_cir("Hello.")
        tl = compile_performance(cir)
        # PRD §14: Simple deterministic timing. 
        # Start=0, Token=0, End=150 per PRD Example §25.
        assert tl.events[0].timestamp_ms == 0
        assert tl.events[1].timestamp_ms == 0
        assert tl.events[2].timestamp_ms == 150

    def test_multi_word_timestamps(self):
        cir = build_cir("Hello world.")
        tl = compile_performance(cir)
        
        # PRD §14 Example: TOKEN 150ms TOKEN 150ms
        # Expected: START(0) -> TOKEN(0) -> TOKEN(150) -> END(300)
        assert len(tl.events) == 4
        assert tl.events[0].event_type == EVENT_SPEAK_START
        assert tl.events[1].event_type == EVENT_TOKEN
        assert tl.events[1].timestamp_ms == 0
        assert tl.events[2].event_type == EVENT_TOKEN
        assert tl.events[2].timestamp_ms == 150
        assert tl.events[3].event_type == EVENT_SPEAK_END
        assert tl.events[3].timestamp_ms == 300

    def test_token_attributes(self):
        cir = build_cir("Hello.")
        tl = compile_performance(cir)
        token_event = tl.events[1]
        
        p = token_event.parameters
        assert p["token"] == "Hello"
        # PRD §13: Initialize ALL attributes to 0.5
        assert p["warmth"] == 0.5
        assert p["energy"] == 0.5
        assert p["confidence"] == 0.5
        assert p["affection"] == 0.5
        assert p["curiosity"] == 0.5
        assert p["playfulness"] == 0.5
        assert p["breathiness"] == 0.5
        assert p["tension"] == 0.5
        assert p["dominance"] == 0.5
        assert p["excitement"] == 0.5

    def test_multiple_utterances(self):
        cir = build_cir("Hello. Goodbye.")
        tl = compile_performance(cir)
        # 2 segments:
        # START(0) -> TOKEN(0) -> TOKEN(150) -> END(300)
        # Wait, does SPEAK_START happen once per timeline or once per segment?
        # PRD §12: "Walk every speech segment. Generate Speak Start -> Tokens -> Speak End".
        # This implies it loops per segment.
        # Segment 1: START(0) -> TOKEN(0) -> END(150)
        # Segment 2: START(150) -> TOKEN(150) -> END(300)
        assert len(tl.events) == 6
        assert tl.events[0].event_type == EVENT_SPEAK_START
        assert tl.events[1].event_type == EVENT_TOKEN
        assert tl.events[2].event_type == EVENT_SPEAK_END
        assert tl.events[3].event_type == EVENT_SPEAK_START
        assert tl.events[4].event_type == EVENT_TOKEN
        assert tl.events[5].event_type == EVENT_SPEAK_END

    def test_determinism_and_uuids(self):
        cir1 = build_cir("Hello world.")
        tl1 = compile_performance(cir1)
        
        cir2 = build_cir("Hello world.")
        tl2 = compile_performance(cir2)
        
        assert tl1.uuid == tl2.uuid
        for e1, e2 in zip(tl1.events, tl2.events):
            assert e1.uuid == e2.uuid

    def test_long_paragraph(self):
        words = ["word"] * 100
        text = " ".join(words) + "."
        cir = build_cir(text)
        tl = compile_performance(cir)
        # 1 segment: START + 100 TOKENS + END = 102 events
        assert len(tl.events) == 102
        assert tl.events[-1].timestamp_ms == 15000  # 100 * 150
