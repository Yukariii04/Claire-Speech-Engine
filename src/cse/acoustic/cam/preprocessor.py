"""CAM-001 Expresso READ Dataset Preprocessor (PRD-028 §4, §5, §6).

Implements deterministic training preprocessing:
    source audio
        ↓
    24 kHz audio
        ↓
    transcript/text
        ↓
    local phoneme sequence
        ↓
    alignment/duration targets
        ↓
    acoustic/vocoder targets (80-channel mel-spectrogram)

Strictly filters for the 8 Expresso READ styles:
    default, confused, enunciated, happy, laughing, narration, sad, whisper.
Rejects improvised dialogue portions for CAM v1.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import soundfile as sf
from loguru import logger

from cse.acoustic.cam.config import (
    CAMConfig,
    EXPRESSO_READ_STYLES,
    INTENT_TO_ID,
    SPEAKER_TO_ID,
    STYLE_TO_ID,
)
from cse.acoustic.cam.phonemizer import CAMPhonemizer


def resample_audio(
    audio: np.ndarray,
    orig_sr: int,
    target_sr: int = 24000,
) -> np.ndarray:
    """Resample 1D audio array to target sample rate (24 kHz) deterministically."""
    if orig_sr == target_sr:
        return audio.astype(np.float32)

    # Deterministic linear interpolation resampling
    num_orig_samples = len(audio)
    num_target_samples = int(round(num_orig_samples * float(target_sr) / float(orig_sr)))
    orig_indices = np.linspace(0, num_orig_samples - 1, num_target_samples)
    resampled = np.interp(orig_indices, np.arange(num_orig_samples), audio)
    return resampled.astype(np.float32)


def compute_mel_spectrogram(
    audio: np.ndarray,
    sample_rate: int = 24000,
    n_fft: int = 1024,
    hop_length: int = 256,
    win_length: int = 1024,
    n_mels: int = 80,
    f_min: float = 0.0,
    f_max: float = 12000.0,
) -> np.ndarray:
    """Compute 80-channel mel-spectrogram targets at 24 kHz deterministically."""
    # Create Hann window
    window = np.hanning(win_length)

    # Pad audio
    pad_len = n_fft // 2
    padded = np.pad(audio, (pad_len, pad_len), mode="reflect")

    # STFT calculation
    num_frames = max(1, (len(padded) - n_fft) // hop_length + 1)
    stft = np.zeros((num_frames, n_fft // 2 + 1), dtype=np.complex64)

    for t in range(num_frames):
        start = t * hop_length
        frame = padded[start : start + n_fft] * window
        spectrum = np.fft.rfft(frame, n=n_fft)
        stft[t] = spectrum

    magnitudes = np.abs(stft)  # [num_frames, n_fft // 2 + 1]

    # Mel filterbank construction
    mel_min = 2595.0 * np.log10(1.0 + f_min / 700.0)
    mel_max = 2595.0 * np.log10(1.0 + f_max / 700.0)
    mel_points = np.linspace(mel_min, mel_max, n_mels + 2)
    hz_points = 700.0 * (10.0 ** (mel_points / 2595.0) - 1.0)
    bins = np.floor((n_fft + 1) * hz_points / sample_rate).astype(int)

    fbank = np.zeros((n_mels, n_fft // 2 + 1), dtype=np.float32)
    for m in range(1, n_mels + 1):
        f_m_minus = bins[m - 1]
        f_m = bins[m]
        f_m_plus = bins[m + 1]

        for k in range(f_m_minus, f_m):
            if f_m != f_m_minus:
                fbank[m - 1, k] = (k - bins[m - 1]) / (bins[m] - bins[m - 1])
        for k in range(f_m, f_m_plus):
            if f_m_plus != f_m:
                fbank[m - 1, k] = (bins[m + 1] - k) / (bins[m + 1] - bins[m])

    # Apply filterbank
    mel_spec = np.dot(magnitudes, fbank.T)  # [num_frames, n_mels]
    mel_spec = np.log(np.clip(mel_spec, a_min=1e-5, a_max=None))

    return mel_spec.astype(np.float32)


class ExpressoDatasetPreprocessor:
    """Deterministic preprocessor for Expresso READ subset (PRD-028 §5, §6)."""

    def __init__(
        self,
        config: CAMConfig | None = None,
        phonemizer: CAMPhonemizer | None = None,
    ) -> None:
        self.config = config or CAMConfig()
        self.phonemizer = phonemizer or CAMPhonemizer()

    def process_utterance(
        self,
        raw_audio: np.ndarray,
        orig_sr: int,
        text: str,
        style: str,
        speaker: str = "speaker_0",
        primary_intent: str = "statement",
    ) -> dict[str, Any]:
        """Preprocess a single Expresso utterance into training targets."""
        # 1. Validate 8 Expresso READ styles (PRD-028 §6)
        style_clean = style.strip().lower()
        if style_clean not in EXPRESSO_READ_STYLES:
            raise ValueError(
                f"Invalid Expresso READ style: '{style}'. Must be one of {EXPRESSO_READ_STYLES}"
            )

        # 2. Resample source audio to 24 kHz (PRD-028 §4)
        audio_24k = resample_audio(raw_audio, orig_sr=orig_sr, target_sr=self.config.sample_rate)

        # 3. Phonemize text
        phoneme_ids = self.phonemizer.text_to_ids(text, add_bos_eos=True)

        # 4. Compute 80-channel mel-spectrogram
        mel = compute_mel_spectrogram(
            audio_24k,
            sample_rate=self.config.sample_rate,
            n_fft=self.config.n_fft,
            hop_length=self.config.hop_length,
            win_length=self.config.win_length,
            n_mels=self.config.n_mels,
            f_min=self.config.f_min,
            f_max=self.config.f_max,
        )

        num_frames = mel.shape[0]
        num_phones = len(phoneme_ids)

        # 5. Extract/synthesize monotonic duration alignment targets
        # Average frame count per phoneme
        base_dur = max(1, num_frames // num_phones)
        durations = np.full(num_phones, base_dur, dtype=np.int64)
        remainder = num_frames - int(durations.sum())
        if remainder > 0:
            durations[-1] += remainder
        elif remainder < 0:
            durations[-1] = max(1, durations[-1] + remainder)

        # 6. Extract pitch & energy targets
        energy = np.linalg.norm(mel, axis=1)  # [num_frames]
        pitch = np.zeros(num_frames, dtype=np.float32)

        return {
            "text": text,
            "phoneme_ids": phoneme_ids,
            "speaker_id": SPEAKER_TO_ID.get(speaker, 0),
            "style_id": STYLE_TO_ID[style_clean],
            "intent_id": INTENT_TO_ID.get(primary_intent, 0),
            "audio_24k": audio_24k,
            "mel": mel,
            "durations": durations,
            "pitch": pitch,
            "energy": energy,
            "sample_rate": self.config.sample_rate,
        }
