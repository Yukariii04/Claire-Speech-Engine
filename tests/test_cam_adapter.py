"""Tests for PerformanceGraph to CAM Conditioning Adapter (PRD-028 §8, §9, §10, §12, §14, §15, §16)."""

import numpy as np
import pytest

from cse.acoustic.cam.adapter import CAMConditioningTensors, GraphToConditioningAdapter
from cse.acoustic.cam.config import (
    CAMConfig,
    CONTOUR_TO_ID,
    EMPHASIS_TO_ID,
    EXPRESSO_READ_STYLES,
    INTENT_TO_ID,
    STYLE_TO_ID,
)
from cse.performance.graph import PerformanceGraph


@pytest.fixture
def adapter():
    return GraphToConditioningAdapter()


@pytest.fixture
def sample_graph():
    return PerformanceGraph(
        text="Hello world, this is a test.",
        character_state={"style": "happy"},
        semantics={"text": "Hello world, this is a test."},
        intent={"primary_intent": "statement", "pace": "moderate", "pitch_contour": "flat", "emphasis": "none"},
        plan={"delivery": {"pace": "moderate", "pitch_contour": "flat", "emphasis": "none"}},
    )


class TestCAMAdapter:
    def test_adapter_produces_conditioning_tensors(self, adapter, sample_graph):
        cond = adapter.adapt(sample_graph)
        assert isinstance(cond, CAMConditioningTensors)
        assert cond.phoneme_ids.ndim == 2
        assert cond.phoneme_ids.shape[0] == 1
        assert cond.phoneme_ids.shape[1] > 2  # Has phonemes + BOS/EOS
        assert cond.speaker_id.shape == (1,)
        assert cond.style_id.shape == (1,)
        assert cond.intent_id.shape == (1,)
        assert cond.pace.shape == (1,)
        assert cond.pitch_contour_id.shape == (1,)
        assert cond.emphasis_id.shape == (1,)

    def test_all_8_expresso_styles_mapped(self, adapter):
        for style_name in EXPRESSO_READ_STYLES:
            graph = PerformanceGraph(
                text="Test style.",
                character_state={"style": style_name},
                semantics={},
                intent={},
                plan={},
            )
            cond = adapter.adapt(graph)
            assert cond.style_id[0] == STYLE_TO_ID[style_name]

    def test_speaker_and_style_remain_separate(self, adapter):
        graph = PerformanceGraph(
            text="Testing separate speaker and style.",
            character_state={"style": "whisper"},
            semantics={},
            intent={},
            plan={},
        )
        cond = adapter.adapt(graph, speaker="speaker_2")
        assert cond.speaker_id[0] == 2
        assert cond.style_id[0] == STYLE_TO_ID["whisper"]
        assert cond.speaker_id[0] != cond.style_id[0]

    def test_primary_intent_mapping(self, adapter):
        for intent_name in ("statement", "question", "exclamation"):
            graph = PerformanceGraph(
                text="Test intent.",
                character_state=None,
                semantics={},
                intent={"primary_intent": intent_name},
                plan={},
            )
            cond = adapter.adapt(graph)
            assert cond.intent_id[0] == INTENT_TO_ID[intent_name]

    def test_pace_mapping(self, adapter):
        paces = {
            "slow": 0.8,
            "moderate": 1.0,
            "fast": 1.25,
            1.5: 1.5,
        }
        for pace_in, expected_pace in paces.items():
            graph = PerformanceGraph(
                text="Test pace.",
                character_state=None,
                semantics={},
                intent={},
                plan={"delivery": {"pace": pace_in}},
            )
            cond = adapter.adapt(graph)
            assert pytest.approx(float(cond.pace[0]), 0.01) == expected_pace

    def test_pitch_contour_mapping(self, adapter):
        contours = ("flat", "rising", "falling", "peaked")
        for c in contours:
            graph = PerformanceGraph(
                text="Test contour.",
                character_state=None,
                semantics={},
                intent={},
                plan={"delivery": {"pitch_contour": c}},
            )
            cond = adapter.adapt(graph)
            assert cond.pitch_contour_id[0] == CONTOUR_TO_ID[c]

    def test_emphasis_mapping(self, adapter):
        emphases = ("none", "final_word", "throughout")
        for e in emphases:
            graph = PerformanceGraph(
                text="Test emphasis.",
                character_state=None,
                semantics={},
                intent={},
                plan={"delivery": {"emphasis": e}},
            )
            cond = adapter.adapt(graph)
            assert cond.emphasis_id[0] == EMPHASIS_TO_ID[e]

    def test_style_vector_injection(self, adapter, sample_graph):
        vec_128 = np.random.randn(1, 128).astype(np.float32)
        cond = adapter.adapt(sample_graph, style_vector=vec_128)
        assert cond.style_vector is not None
        assert cond.style_vector.shape == (1, 128)

    def test_invalid_style_vector_dimension_raises(self, adapter, sample_graph):
        vec_invalid = np.random.randn(1, 64).astype(np.float32)
        with pytest.raises(ValueError, match="Style vector dimension mismatch"):
            adapter.adapt(sample_graph, style_vector=vec_invalid)

    def test_rejects_non_performance_graph(self, adapter):
        with pytest.raises(TypeError):
            adapter.adapt("not a performance graph")
