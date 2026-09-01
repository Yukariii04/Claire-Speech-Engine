"""PerformanceGraph to CAM Conditioning Adapter (PRD-028 §8, §9, §10, §12, §14, §15, §16).

Maps the frozen PerformanceGraph produced by CPE to the continuous and discrete
conditioning tensors consumed by CAM-001.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

from cse.acoustic.cam.config import (
    CAMConfig,
    CONTOUR_TO_ID,
    EMPHASIS_TO_ID,
    EXPRESSO_READ_STYLES,
    INTENT_TO_ID,
    SPEAKER_TO_ID,
    STYLE_TO_ID,
)
from cse.acoustic.cam.phonemizer import CAMPhonemizer
from cse.performance.graph import PerformanceGraph


@dataclass(frozen=True)
class CAMConditioningTensors:
    """Immutable bundle of conditioning tensors prepared for CAM acoustic trunk."""

    phoneme_ids: np.ndarray        # [1, T_phoneme] int64
    speaker_id: np.ndarray         # [1] int64
    style_id: np.ndarray           # [1] int64
    intent_id: np.ndarray          # [1] int64
    pace: np.ndarray               # [1] float32
    pitch_contour_id: np.ndarray   # [1] int64
    emphasis_id: np.ndarray        # [1] int64
    style_vector: np.ndarray | None = None  # [1, 128] float32 (optional direct vector)


class GraphToConditioningAdapter:
    """Translates a PerformanceGraph into CAM-001 acoustic conditioning."""

    def __init__(
        self,
        config: CAMConfig | None = None,
        phonemizer: CAMPhonemizer | None = None,
    ) -> None:
        self.config = config or CAMConfig()
        self.phonemizer = phonemizer or CAMPhonemizer()

    def map_pace(self, pace_val: Any) -> float:
        """Map CPE pace specification to a duration scaling factor."""
        if pace_val is None:
            return float(self.config.default_pace)
        if isinstance(pace_val, (int, float)):
            return max(0.2, min(3.0, float(pace_val)))
        if isinstance(pace_val, str):
            p = pace_val.strip().lower()
            if p == "slow":
                return 0.8
            elif p == "fast":
                return 1.25
            elif p == "moderate":
                return 1.0
        return float(self.config.default_pace)

    def map_style(self, style_val: Any) -> int:
        """Map style name to Expresso style ID (0..7)."""
        if style_val is None:
            return STYLE_TO_ID[self.config.default_style]
        if isinstance(style_val, int):
            return style_val % len(EXPRESSO_READ_STYLES)
        if isinstance(style_val, str):
            s = style_val.strip().lower()
            return STYLE_TO_ID.get(s, STYLE_TO_ID[self.config.default_style])
        return STYLE_TO_ID[self.config.default_style]

    def map_speaker(self, speaker_val: Any) -> int:
        """Map speaker name to speaker ID."""
        if speaker_val is None:
            return SPEAKER_TO_ID[self.config.default_speaker]
        if isinstance(speaker_val, int):
            return speaker_val
        if isinstance(speaker_val, str):
            spk = speaker_val.strip().lower()
            return SPEAKER_TO_ID.get(spk, 0)
        return 0

    def map_primary_intent(self, intent_val: Any) -> int:
        """Map CPE primary_intent to intent ID (statement=0, question=1, exclamation=2)."""
        if intent_val is None:
            return INTENT_TO_ID[self.config.default_intent]
        if isinstance(intent_val, int):
            return intent_val % len(INTENT_TO_ID)
        if isinstance(intent_val, str):
            i = intent_val.strip().lower()
            return INTENT_TO_ID.get(i, INTENT_TO_ID[self.config.default_intent])
        return INTENT_TO_ID[self.config.default_intent]

    def map_pitch_contour(self, contour_val: Any) -> int:
        """Map CPE pitch_contour to contour ID (flat=0, rising=1, falling=2, peaked=3)."""
        if contour_val is None:
            return CONTOUR_TO_ID[self.config.default_contour]
        if isinstance(contour_val, int):
            return contour_val % len(CONTOUR_TO_ID)
        if isinstance(contour_val, str):
            c = contour_val.strip().lower()
            return CONTOUR_TO_ID.get(c, CONTOUR_TO_ID[self.config.default_contour])
        return CONTOUR_TO_ID[self.config.default_contour]

    def map_emphasis(self, emphasis_val: Any) -> int:
        """Map CPE emphasis to emphasis ID (none=0, final_word=1, throughout=2)."""
        if emphasis_val is None:
            return EMPHASIS_TO_ID[self.config.default_emphasis]
        if isinstance(emphasis_val, int):
            return emphasis_val % len(EMPHASIS_TO_ID)
        if isinstance(emphasis_val, str):
            e = emphasis_val.strip().lower()
            return EMPHASIS_TO_ID.get(e, EMPHASIS_TO_ID[self.config.default_emphasis])
        return EMPHASIS_TO_ID[self.config.default_emphasis]

    def adapt(
        self,
        graph: PerformanceGraph,
        speaker: str | int | None = None,
        style_override: str | int | None = None,
        style_vector: np.ndarray | None = None,
    ) -> CAMConditioningTensors:
        """Convert a PerformanceGraph into CAM conditioning tensors.

        Args:
            graph: Canonical PerformanceGraph from CPE.
            speaker: Optional speaker ID override.
            style_override: Optional explicit style override.
            style_vector: Optional explicit 128-d style embedding vector.

        Returns:
            CAMConditioningTensors ready for inference.
        """
        if not isinstance(graph, PerformanceGraph):
            raise TypeError(f"Expected PerformanceGraph, got {type(graph).__name__}")

        # 1. Phonemize text
        phoneme_ids_list = self.phonemizer.text_to_ids(graph.text, add_bos_eos=True)
        if not phoneme_ids_list:
            # Fallback for empty text
            phoneme_ids_list = [self.phonemizer.phonemes_to_ids([])]  # BOS + EOS

        phoneme_ids = np.array([phoneme_ids_list], dtype=np.int64)

        # 2. Speaker conditioning
        spk_id_val = self.map_speaker(speaker)
        speaker_id = np.array([spk_id_val], dtype=np.int64)

        # 3. Style conditioning (default or from character_state or override)
        style_raw = style_override
        if style_raw is None and isinstance(graph.character_state, dict):
            style_raw = graph.character_state.get("style")
        style_id_val = self.map_style(style_raw)
        style_id = np.array([style_id_val], dtype=np.int64)

        # 4. Primary Intent conditioning (PRD-028 §12)
        intent_dict = graph.intent if isinstance(graph.intent, dict) else {}
        primary_intent_raw = intent_dict.get("primary_intent")
        intent_id_val = self.map_primary_intent(primary_intent_raw)
        intent_id = np.array([intent_id_val], dtype=np.int64)

        # 5. Delivery plan controls (pace, pitch_contour, emphasis)
        plan_dict = graph.plan if isinstance(graph.plan, dict) else {}
        delivery_dict = plan_dict.get("delivery", {}) if isinstance(plan_dict, dict) else {}

        pace_raw = delivery_dict.get("pace", intent_dict.get("pace"))
        pace_val = self.map_pace(pace_raw)
        pace = np.array([pace_val], dtype=np.float32)

        contour_raw = delivery_dict.get("pitch_contour", intent_dict.get("pitch_contour"))
        contour_val = self.map_pitch_contour(contour_raw)
        pitch_contour_id = np.array([contour_val], dtype=np.int64)

        emphasis_raw = delivery_dict.get("emphasis", intent_dict.get("emphasis"))
        emphasis_val = self.map_emphasis(emphasis_raw)
        emphasis_id = np.array([emphasis_val], dtype=np.int64)

        # Optional style vector check (must be 128-d if provided)
        if style_vector is not None:
            style_vector = np.asarray(style_vector, dtype=np.float32)
            if style_vector.ndim == 1:
                style_vector = np.expand_dims(style_vector, axis=0)
            if style_vector.shape[-1] != self.config.style_dim:
                raise ValueError(
                    f"Style vector dimension mismatch: expected {self.config.style_dim}, got {style_vector.shape[-1]}"
                )

        return CAMConditioningTensors(
            phoneme_ids=phoneme_ids,
            speaker_id=speaker_id,
            style_id=style_id,
            intent_id=intent_id,
            pace=pace,
            pitch_contour_id=pitch_contour_id,
            emphasis_id=emphasis_id,
            style_vector=style_vector,
        )
