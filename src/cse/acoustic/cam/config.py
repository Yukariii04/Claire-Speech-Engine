"""CAM-001 Configuration and Architectural Constants (PRD-028)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


# Supported 8 Expresso Read-Speech Styles (PRD-028 §6)
EXPRESSO_READ_STYLES: tuple[str, ...] = (
    "default",
    "confused",
    "enunciated",
    "happy",
    "laughing",
    "narration",
    "sad",
    "whisper",
)

STYLE_TO_ID: dict[str, int] = {style: idx for idx, style in enumerate(EXPRESSO_READ_STYLES)}
ID_TO_STYLE: dict[int, str] = {idx: style for idx, style in enumerate(EXPRESSO_READ_STYLES)}

# Primary Intent Categories (PRD-028 §12)
PRIMARY_INTENTS: tuple[str, ...] = (
    "statement",
    "question",
    "exclamation",
)

INTENT_TO_ID: dict[str, int] = {intent: idx for idx, intent in enumerate(PRIMARY_INTENTS)}
ID_TO_INTENT: dict[int, str] = {idx: intent for idx, intent in enumerate(PRIMARY_INTENTS)}

# Pitch Contour Categories (PRD-028 §15)
PITCH_CONTOURS: tuple[str, ...] = (
    "flat",
    "rising",
    "falling",
    "peaked",
)

CONTOUR_TO_ID: dict[str, int] = {contour: idx for idx, contour in enumerate(PITCH_CONTOURS)}
ID_TO_CONTOUR: dict[int, str] = {idx: contour for idx, contour in enumerate(PITCH_CONTOURS)}

# Emphasis Categories (PRD-028 §16)
EMPHASIS_TYPES: tuple[str, ...] = (
    "none",
    "final_word",
    "throughout",
)

EMPHASIS_TO_ID: dict[str, int] = {emphasis: idx for idx, emphasis in enumerate(EMPHASIS_TYPES)}
ID_TO_EMPHASIS: dict[int, str] = {idx: emphasis for idx, emphasis in enumerate(EMPHASIS_TYPES)}

# Expresso Speaker IDs
EXPRESSO_SPEAKERS: tuple[str, ...] = (
    "speaker_0",
    "speaker_1",
    "speaker_2",
    "speaker_3",
)

SPEAKER_TO_ID: dict[str, int] = {spk: idx for idx, spk in enumerate(EXPRESSO_SPEAKERS)}
ID_TO_SPEAKER: dict[int, str] = {idx: spk for idx, spk in enumerate(EXPRESSO_SPEAKERS)}


@dataclass(frozen=True)
class CAMConfig:
    """Configuration for the Claire Acoustic Model (CAM-001)."""

    # Audio targets (PRD-028 §4, PRD-029 §9)
    sample_rate: int = 24000
    n_fft: int = 1024
    win_length: int = 1024
    hop_length: int = 256
    n_mels: int = 100  # Locked Vocos-compatible target (PRD-029 §9)
    f_min: float = 0.0
    f_max: float = 12000.0

    # Model architecture dimensions (PRD-028 §7-13)
    vocab_size: int = 256
    d_model: int = 192
    encoder_layers: int = 4
    encoder_heads: int = 4
    decoder_layers: int = 4
    decoder_heads: int = 4
    conv_filter_size: int = 768
    conv_kernel_size: int = 5
    dropout: float = 0.1

    # Conditioning dimensions (PRD-028 §7, §8, §9, §10, §12)
    style_dim: int = 128            # PRD-028 §7: Strictly 128-dimensional interface
    speaker_dim: int = 64          # PRD-028 §8: Practical dimension (64-d)
    intent_dim: int = 32           # PRD-028 §12: Implementation-defined (32-d)
    contour_dim: int = 32          # PRD-028 §15: Learned contour representation (32-d)
    emphasis_dim: int = 16         # PRD-028 §16: Learned emphasis representation (16-d)

    # Defaults
    default_speaker: str = "speaker_0"
    default_style: str = "default"
    default_intent: str = "statement"
    default_pace: float = 1.0
    default_contour: str = "flat"
    default_emphasis: str = "none"

    # Runtime and Artifact paths
    acoustic_model_path: Path | str | None = None
    vocoder_model_path: Path | str | None = None
    quantized_acoustic_path: Path | str | None = None
    quantized_vocoder_path: Path | str | None = None
    output_dir: Path | str = field(default_factory=lambda: Path("output/cam"))
    cache_dir: Path | str = field(default_factory=lambda: Path.home() / ".cache" / "claire" / "cam")
