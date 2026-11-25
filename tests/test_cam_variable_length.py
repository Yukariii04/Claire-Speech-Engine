"""Regression tests for Variable-Length Length Regulation in CAM-001."""

from __future__ import annotations

import torch

from cse.acoustic.cam.acoustic_model import CamAcousticModel
from cse.acoustic.cam.config import CAMConfig
from cse.acoustic.cam.modules.variance_adaptor import LengthRegulator, VarianceAdaptor


class TestVariableLengthRegulation:
    """Validate padding-aware length regulation and variable-length acoustic forward."""

    def test_length_regulator_variable_length_padding_awareness(self):
        """Verify padded phone positions contribute zero frames during expansion."""
        lr = LengthRegulator()
        D = 64

        durations = torch.tensor(
            [
                [3, 2, 4, 1, 0, 0, 0],
                [2, 1, 2, 3, 2, 1, 2],
            ],
            dtype=torch.long,
        )
        phoneme_lens = torch.tensor([4, 7], dtype=torch.long)
        x = torch.randn(2, 7, D)

        expanded = lr(x, durations, phoneme_lens=phoneme_lens)

        assert expanded.shape == (2, 13, D)
        assert durations[0, :phoneme_lens[0]].sum().item() == 10
        assert torch.all(expanded[0, 10:] == 0.0), "Padded frames in sample 0 must be zero"
        assert not torch.all(expanded[0, :10] == 0.0), "Real frames in sample 0 must not be zero"

        for f in range(0, 3):
            assert torch.allclose(expanded[0, f], x[0, 0])
        for f in range(3, 5):
            assert torch.allclose(expanded[0, f], x[0, 1])
        for f in range(5, 9):
            assert torch.allclose(expanded[0, f], x[0, 2])
        assert torch.allclose(expanded[0, 9], x[0, 3])
        assert not torch.all(expanded[1, 12] == 0.0)

    def test_variance_adaptor_variable_length(self):
        """Verify VarianceAdaptor masks predicted durations on padded phoneme positions."""
        va = VarianceAdaptor(d_model=192)
        B, T_phone, D = 2, 6, 192

        enc_out = torch.randn(B, T_phone, D)
        pace = torch.tensor([1.0, 1.0], dtype=torch.float32)
        pitch_contour_id = torch.tensor([0, 0], dtype=torch.long)
        emphasis_id = torch.tensor([0, 0], dtype=torch.long)
        phoneme_lens = torch.tensor([4, 6], dtype=torch.long)

        _, dur_pred, _, _, _ = va(
            encoder_output=enc_out,
            pace=pace,
            pitch_contour_id=pitch_contour_id,
            emphasis_id=emphasis_id,
            phoneme_lens=phoneme_lens,
        )

        assert (dur_pred[0, :4] >= 1).all()
        assert (dur_pred[1, :6] >= 1).all()
        assert (dur_pred[0, 4:] == 0).all()

    def test_acoustic_model_variable_length_forward(self):
        """Verify CamAcousticModel supports padded variable-length batches."""
        model = CamAcousticModel(CAMConfig(d_model=128, n_mels=100)).eval()
        phoneme_ids = torch.tensor(
            [
                [2, 10, 15, 3, 0, 0, 0],
                [2, 10, 15, 20, 25, 30, 3],
            ],
            dtype=torch.long,
        )
        durations = torch.tensor(
            [
                [5, 5, 5, 5, 0, 0, 0],
                [5, 5, 5, 5, 5, 5, 5],
            ],
            dtype=torch.long,
        )
        phoneme_lens = torch.tensor([4, 7], dtype=torch.long)

        with torch.no_grad():
            out = model(
                phoneme_ids=phoneme_ids,
                speaker_id=torch.tensor([0, 1], dtype=torch.long),
                style_id=torch.tensor([0, 3], dtype=torch.long),
                intent_id=torch.tensor([0, 0], dtype=torch.long),
                pace=torch.tensor([1.0, 1.0], dtype=torch.float32),
                pitch_contour_id=torch.tensor([0, 1], dtype=torch.long),
                emphasis_id=torch.tensor([0, 2], dtype=torch.long),
                target_durations=durations,
                phoneme_lens=phoneme_lens,
            )

        assert out.mel.shape == (2, 35, 100)
