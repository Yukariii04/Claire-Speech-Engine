"""Tests for CAM-001 Expresso READ Preprocessor and Dataset (PRD-028 §4, §5, §6)."""

import numpy as np
import pytest
import torch

from cse.acoustic.cam.config import EXPRESSO_READ_STYLES
from cse.acoustic.cam.dataset import ExpressoReadDataset, collate_cam_batch
from cse.acoustic.cam.preprocessor import (
    ExpressoDatasetPreprocessor,
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
        mel = compute_mel_spectrogram(audio, sample_rate=24000, n_mels=80, hop_length=256)
        assert mel.ndim == 2
        assert mel.shape[1] == 80
        # Expected frames ~ 12000 // 256 + 1 = 47
        assert abs(mel.shape[0] - 47) <= 2

    def test_preprocessor_accepts_8_read_styles(self):
        prep = ExpressoDatasetPreprocessor()
        raw_audio = np.random.randn(24000).astype(np.float32)
        for style in EXPRESSO_READ_STYLES:
            res = prep.process_utterance(
                raw_audio=raw_audio,
                orig_sr=24000,
                text="A sample sentence for preprocessing.",
                style=style,
                speaker="speaker_0",
            )
            assert res["sample_rate"] == 24000
            assert res["mel"].shape[1] == 80
            assert len(res["phoneme_ids"]) == len(res["durations"])

    def test_preprocessor_rejects_non_read_styles(self):
        prep = ExpressoDatasetPreprocessor()
        raw_audio = np.random.randn(24000).astype(np.float32)
        with pytest.raises(ValueError, match="Invalid Expresso READ style"):
            prep.process_utterance(
                raw_audio=raw_audio,
                orig_sr=24000,
                text="Test.",
                style="improvised_dialogue_style",
            )

    def test_pytorch_dataset_and_batch_collation(self):
        prep = ExpressoDatasetPreprocessor()
        items = []
        for i, text in enumerate(["Short.", "A bit longer sentence.", "Third test utterance with more words."]):
            raw_audio = np.random.randn(24000 * (i + 1) // 2).astype(np.float32)
            processed = prep.process_utterance(
                raw_audio=raw_audio,
                orig_sr=24000,
                text=text,
                style=EXPRESSO_READ_STYLES[i % len(EXPRESSO_READ_STYLES)],
            )
            items.append(processed)

        dataset = ExpressoReadDataset(items)
        assert len(dataset) == 3

        batch = [dataset[0], dataset[1], dataset[2]]
        collated = collate_cam_batch(batch)

        assert collated["phoneme_ids"].shape[0] == 3
        assert collated["mel"].shape[0] == 3
        assert collated["mel"].shape[2] == 80
        assert collated["durations"].shape[0] == 3
        assert collated["speaker_id"].shape[0] == 3
        assert collated["style_id"].shape[0] == 3
        assert collated["intent_id"].shape[0] == 3
