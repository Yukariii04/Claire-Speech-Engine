"""Regression tests for Variable-Length Length Regulation and Dataset Contracts (PRD-029 Correction 6)."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
import torch
import torch.nn.functional as F

from cse.acoustic.cam.acoustic_model import CamAcousticModel
from cse.acoustic.cam.config import CAMConfig, EXPRESSO_READ_STYLES, EXPRESSO_SPEAKERS
from cse.acoustic.cam.modules.variance_adaptor import LengthRegulator, VarianceAdaptor
from cse.training.cam.dataset import ExpressoTrainingDataset, collate_training_batch
from cse.training.cam.trainer import CamTrainer, TrainingConfig
from cse.training.cam.validate_dataset import validate_dataset_conditioning


class TestVariableLengthRegulation:
    """Validate padding-aware length regulation and variable-length training batches."""

    def test_length_regulator_variable_length_padding_awareness(self):
        """Verify:
        - at least two samples having different phoneme lengths
        - sum of expanded frames for each sample == sum of real durations for that sample
        - padded phones contribute exactly zero frames
        """
        lr = LengthRegulator()
        D = 64

        # Sample 0: 4 real phones (durations [3, 2, 4, 1] -> sum=10), padded to 7
        # Sample 1: 7 real phones (durations [2, 1, 2, 3, 2, 1, 2] -> sum=13)
        durations = torch.tensor(
            [
                [3, 2, 4, 1, 0, 0, 0],
                [2, 1, 2, 3, 2, 1, 2],
            ],
            dtype=torch.long,
        )
        phoneme_lens = torch.tensor([4, 7], dtype=torch.long)

        # Distinct feature representations for each phoneme
        x = torch.randn(2, 7, D)

        expanded = lr(x, durations, phoneme_lens=phoneme_lens)

        # Total frames must match max duration sum across batch (max(10, 13) = 13)
        assert expanded.shape == (2, 13, D)

        # Sample 0:
        # Sum of real durations = 3 + 2 + 4 + 1 = 10
        real_dur_sum_0 = durations[0, :phoneme_lens[0]].sum().item()
        assert real_dur_sum_0 == 10

        # Padded phone positions (4, 5, 6) must contribute zero frames.
        # Frames 0..9 correspond to the real phones; frames 10..12 should be zero
        assert torch.all(expanded[0, 10:] == 0.0), "Padded frames in sample 0 must be zero"
        assert not torch.all(expanded[0, :10] == 0.0), "Real frames in sample 0 must not be zero"

        # Frame breakdown for sample 0:
        # frames 0..2 match x[0, 0]
        for f in range(0, 3):
            assert torch.allclose(expanded[0, f], x[0, 0])
        # frames 3..4 match x[0, 1]
        for f in range(3, 5):
            assert torch.allclose(expanded[0, f], x[0, 1])
        # frames 5..8 match x[0, 2]
        for f in range(5, 9):
            assert torch.allclose(expanded[0, f], x[0, 2])
        # frame 9 matches x[0, 3]
        assert torch.allclose(expanded[0, 9], x[0, 3])

        # Sample 1:
        # Sum of real durations = 2 + 1 + 2 + 3 + 2 + 1 + 2 = 13
        real_dur_sum_1 = durations[1, :phoneme_lens[1]].sum().item()
        assert real_dur_sum_1 == 13

        # All 13 frames must be non-zero and match sequence
        assert not torch.all(expanded[1, 12] == 0.0)

    def test_variance_adaptor_variable_length(self):
        """Verify VarianceAdaptor correctly handles variable phoneme lengths and masks padded durations."""
        va = VarianceAdaptor(d_model=192)
        B, T_phone, D = 2, 6, 192

        enc_out = torch.randn(B, T_phone, D)
        pace = torch.tensor([1.0, 1.0], dtype=torch.float32)
        pitch_contour_id = torch.tensor([0, 0], dtype=torch.long)
        emphasis_id = torch.tensor([0, 0], dtype=torch.long)
        phoneme_lens = torch.tensor([4, 6], dtype=torch.long)

        # Inference mode (predicted durations)
        out_hid, dur_pred, log_dur, pitch_pred, energy_pred = va(
            encoder_output=enc_out,
            pace=pace,
            pitch_contour_id=pitch_contour_id,
            emphasis_id=emphasis_id,
            phoneme_lens=phoneme_lens,
        )

        # Real phones must have duration >= 1
        assert (dur_pred[0, :4] >= 1).all()
        assert (dur_pred[1, :6] >= 1).all()

        # Padded phone positions must have duration == 0
        assert (dur_pred[0, 4:] == 0).all()

    def test_acoustic_model_and_trainer_variable_length_batch(self, tmp_path):
        """Verify that CamAcousticModel and CamTrainer execute complete forward/backward on variable-length batches."""
        # 1. Acoustic Model Forward
        model = CamAcousticModel(CAMConfig(d_model=128, n_mels=100))

        batch_items = [
            {
                "sample_id": "sample_short",
                "phoneme_ids": np.array([2, 10, 15, 3], dtype=np.int64),
                "speaker": "speaker_0",
                "style": "default",
                "primary_intent": "statement",
                "pace": 1.0,
                "pitch_contour": "flat",
                "emphasis": "none",
                "mel": np.random.randn(20, 100).astype(np.float32),
                "durations": np.array([5, 5, 5, 5], dtype=np.int64),
                "log_durations": np.log(np.array([5, 5, 5, 5], dtype=np.float32) + 1.0),
                "f0": np.ones(20, dtype=np.float32) * 150.0,
                "log_f0": np.log(np.ones(20, dtype=np.float32) * 150.0),
                "energy": np.ones(20, dtype=np.float32),
                "voiced_mask": np.ones(20, dtype=bool),
            },
            {
                "sample_id": "sample_long",
                "phoneme_ids": np.array([2, 10, 15, 20, 25, 30, 3], dtype=np.int64),
                "speaker": "speaker_1",
                "style": "happy",
                "primary_intent": "statement",
                "pace": 1.0,
                "pitch_contour": "rising",
                "emphasis": "moderate",
                "mel": np.random.randn(35, 100).astype(np.float32),
                "durations": np.array([5, 5, 5, 5, 5, 5, 5], dtype=np.int64),
                "log_durations": np.log(np.array([5, 5, 5, 5, 5, 5, 5], dtype=np.float32) + 1.0),
                "f0": np.ones(35, dtype=np.float32) * 200.0,
                "log_f0": np.log(np.ones(35, dtype=np.float32) * 200.0),
                "energy": np.ones(35, dtype=np.float32),
                "voiced_mask": np.ones(35, dtype=bool),
            },
        ]

        dataset = ExpressoTrainingDataset(batch_items)
        batch = collate_training_batch([dataset[0], dataset[1]])

        assert batch["phoneme_lens"].tolist() == [4, 7]
        assert batch["durations"][0, 4:].sum().item() == 0

        # Model forward
        out = model(
            phoneme_ids=batch["phoneme_ids"],
            speaker_id=batch["speaker_id"],
            style_id=batch["style_id"],
            intent_id=batch["intent_id"],
            pace=batch["pace"],
            pitch_contour_id=batch["pitch_contour_id"],
            emphasis_id=batch["emphasis_id"],
            target_durations=batch["durations"],
            phoneme_lens=batch["phoneme_lens"],
        )

        assert out.mel.shape == (2, 35, 100)

        # 2. Complete Trainer Step with variable-length batch
        trainer = CamTrainer(
            model=model,
            train_dataset=dataset,
            val_dataset=dataset,
            config=TrainingConfig(
                epochs=1,
                batch_size=2,
                learning_rate=1e-3,
                checkpoint_dir=str(tmp_path / "checkpoints"),
                device="cpu",
            ),
        )

        epoch_loss = trainer.train_epoch()
        assert "total_loss" in epoch_loss
        assert not np.isnan(epoch_loss["total_loss"])

        val_loss = trainer.evaluate()
        assert "total_loss" in val_loss
        assert not np.isnan(val_loss["total_loss"])


class TestDatasetContract:
    """Validate serious dataset contract enforcement."""

    def test_contract_passes_on_balanced_dataset(self, tmp_path):
        """Balanced 32-pair index must pass contract validation."""
        index_file = tmp_path / "dataset_index.json"
        samples = []
        for spk in EXPRESSO_SPEAKERS:
            for sty in EXPRESSO_READ_STYLES:
                for idx in range(2):  # 2 per pair for test
                    samples.append({
                        "sample_id": f"{spk}_{sty}_{idx}",
                        "speaker": spk,
                        "style": sty,
                        "primary_intent": "statement",
                        "pitch_contour": "flat",
                        "emphasis": "none",
                        "pace": 1.0,
                        "audio_source": "expresso_real",
                        "provenance": "ylacombe/expresso (real)",
                    })

        index_data = {
            "is_synthetic_smoke": False,
            "samples": {"train": samples, "val": [], "test": []},
        }
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index_data, f)

        report = validate_dataset_conditioning(
            index_file,
            expected_total=len(samples),
            expected_speakers=EXPRESSO_SPEAKERS,
            expected_styles=EXPRESSO_READ_STYLES,
            expected_per_pair=2,
        )
        assert report["status"] == "PASS"

    def test_contract_fails_on_deficit_pair(self, tmp_path):
        """Missing or deficit pair must fail loudly with detailed report."""
        index_file = tmp_path / "dataset_index.json"
        samples = []
        for spk in EXPRESSO_SPEAKERS:
            for sty in EXPRESSO_READ_STYLES:
                count = 1 if (spk == "speaker_0" and sty == "whisper") else 2
                for idx in range(count):
                    samples.append({
                        "sample_id": f"{spk}_{sty}_{idx}",
                        "speaker": spk,
                        "style": sty,
                        "primary_intent": "statement",
                        "pitch_contour": "flat",
                        "emphasis": "none",
                        "pace": 1.0,
                        "audio_source": "expresso_real",
                        "provenance": "ylacombe/expresso (real)",
                    })

        index_data = {
            "is_synthetic_smoke": False,
            "samples": {"train": samples, "val": [], "test": []},
        }
        with open(index_file, "w", encoding="utf-8") as f:
            json.dump(index_data, f)

        report = validate_dataset_conditioning(
            index_file,
            expected_total=64,
            expected_speakers=EXPRESSO_SPEAKERS,
            expected_styles=EXPRESSO_READ_STYLES,
            expected_per_pair=2,
        )
        assert report["status"] == "FAIL"
        assert "Serious dataset contract failed" in report["status_detail"]
        assert "speaker_0/whisper" in report["status_detail"]
