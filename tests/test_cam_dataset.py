"""Tests for CAM-001 Expresso READ Preprocessor and Dataset (PRD-028 §4, §5, §6)."""

import numpy as np
import pytest
import torch

from cse.acoustic.cam.config import EXPRESSO_READ_STYLES
from cse.training.cam.dataset import ExpressoTrainingDataset, collate_training_batch
from cse.acoustic.cam.preprocessor import (
    compute_mel_spectrogram,
    resample_audio,
)


class TestCAMDataset:
    def test_resample_audio_to_24khz(self):
        # 1 second of 16 kHz sine wave
        t = np.linspace(0, 1.0, 16000)
        audio_16k = np.sin(2 * np.pi * 440 * t).astype(np.float32)
        resampled_24k = resample_audio(audio_16k, orig_sr=16000, target_sr=24000)
        assert len(resampled_24k) == 24000
        assert resampled_24k.dtype == np.float32

    def test_compute_mel_spectrogram_shape(self):
        # 0.5s of 24 kHz noise
        audio = np.random.randn(12000).astype(np.float32)
        mel = compute_mel_spectrogram(audio, sample_rate=24000, n_mels=100, hop_length=256)
        assert mel.ndim == 2
        assert mel.shape[1] == 100
        # Expected frames ~ 12000 // 256 + 1 = 47
        assert abs(mel.shape[0] - 47) <= 2

    def test_pytorch_dataset_and_batch_collation(self):
        items = []
        # Create 3 variable-length samples
        lengths = [(5, 20), (8, 35), (12, 50)]
        for i, (n_phones, n_frames) in enumerate(lengths):
            phoneme_ids = np.random.randint(1, 100, size=n_phones, dtype=np.int64)
            # Realistic integer durations summing to n_frames
            base = n_frames // n_phones
            durations = np.full(n_phones, base, dtype=np.int64)
            durations[-1] += (n_frames - int(durations.sum()))

            mel = np.random.randn(n_frames, 100).astype(np.float32)
            items.append({
                "sample_id": f"sample_{i}",
                "phoneme_ids": phoneme_ids,
                "speaker": "speaker_0",
                "style": EXPRESSO_READ_STYLES[i % len(EXPRESSO_READ_STYLES)],
                "primary_intent": "statement",
                "pace": 1.0,
                "pitch_contour": "flat",
                "emphasis": "none",
                "mel": mel,
                "durations": durations,
                "log_durations": np.log(np.maximum(durations.astype(np.float32), 1.0)),
                "f0": np.zeros(n_frames, dtype=np.float32),
                "log_f0": np.zeros(n_frames, dtype=np.float32),
                "energy": np.zeros(n_frames, dtype=np.float32),
                "voiced_mask": np.zeros(n_frames, dtype=bool),
            })

        dataset = ExpressoTrainingDataset(items)
        assert len(dataset) == 3

        batch = [dataset[0], dataset[1], dataset[2]]
        collated = collate_training_batch(batch)

        assert collated["phoneme_ids"].shape == (3, 12)
        assert collated["phoneme_lens"].tolist() == [5, 8, 12]
        assert collated["mel"].shape == (3, 50, 100)
        assert collated["mel_lens"].tolist() == [20, 35, 50]
        assert collated["durations"].shape == (3, 12)
        assert collated["speaker_id"].shape[0] == 3
        assert collated["style_id"].shape[0] == 3
        assert collated["intent_id"].shape[0] == 3

