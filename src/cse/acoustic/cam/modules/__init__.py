"""CAM-001 Neural Modules Package (PRD-028)."""

from cse.acoustic.cam.modules.conditioning import (
    LearnedEmphasisConditioning,
    LearnedPitchContourConditioning,
    PrimaryIntentEmbedding,
    SpeakerEmbedding,
    SpeakerStyleMixer,
    StyleEmbedding,
)
from cse.acoustic.cam.modules.decoder import AcousticDecoder
from cse.acoustic.cam.modules.encoder import PhonemeEncoder
from cse.acoustic.cam.modules.variance_adaptor import LengthRegulator, VarianceAdaptor

__all__ = [
    "StyleEmbedding",
    "SpeakerEmbedding",
    "SpeakerStyleMixer",
    "PrimaryIntentEmbedding",
    "LearnedPitchContourConditioning",
    "LearnedEmphasisConditioning",
    "PhonemeEncoder",
    "VarianceAdaptor",
    "LengthRegulator",
    "AcousticDecoder",
]
