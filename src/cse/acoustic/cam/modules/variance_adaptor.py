"""CAM-001 FastSpeech2-Style Variance Adaptor (PRD-028 §2, §12, §13, §14, §15, §16, §18).

Implements:
- Duration Predictor & Matrix Length Regulator with dynamic ONNX export support.
- Learned Pitch Contour sequence-aligned conditioning & Pitch Predictor.
- Learned Energy / Emphasis sequence-aligned conditioning & Energy Predictor.
- Pace-to-duration scaling (no post-generation DSP time-stretching).
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from cse.acoustic.cam.modules.conditioning import (
    LearnedEmphasisConditioning,
    LearnedPitchContourConditioning,
)


class VariancePredictor(nn.Module):
    """Convolutional predictor for duration, pitch, or energy."""

    def __init__(
        self,
        d_model: int = 192,
        conv_filter_size: int = 256,
        kernel_size: int = 3,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        padding = (kernel_size - 1) // 2
        self.conv1 = nn.Conv1d(d_model, conv_filter_size, kernel_size=kernel_size, padding=padding)
        self.norm1 = nn.LayerNorm(conv_filter_size)
        self.dropout1 = nn.Dropout(dropout)

        self.conv2 = nn.Conv1d(conv_filter_size, conv_filter_size, kernel_size=kernel_size, padding=padding)
        self.norm2 = nn.LayerNorm(conv_filter_size)
        self.dropout2 = nn.Dropout(dropout)

        self.linear = nn.Linear(conv_filter_size, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, T, d_model]
        h = x.transpose(1, 2)
        h = F.relu(self.conv1(h))
        h = self.norm1(h.transpose(1, 2)).transpose(1, 2)
        h = self.dropout1(h)

        h = F.relu(self.conv2(h))
        h = self.norm2(h.transpose(1, 2))
        h = self.dropout2(h)

        out = self.linear(h)
        return out.squeeze(-1)  # [B, T]


class LengthRegulator(nn.Module):
    """Dynamic Matrix Length Regulator expanding phonemes to acoustic frames (PRD-028 §18).

    Uses vectorized cumulative sum range comparison and matrix multiplication.
    100% dynamic ONNX compatible.
    """

    def forward(
        self,
        x: torch.Tensor,
        durations: torch.Tensor,
        phoneme_lens: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """Expand phoneme sequence x [B, T_phone, D] according to durations [B, T_phone]."""
        B, T_phone = durations.shape

        if phoneme_lens is not None:
            phone_range = torch.arange(T_phone, device=durations.device).view(1, -1)
            real_mask = phone_range < phoneme_lens.view(B, 1)
            real_dur = torch.clamp(durations, min=1)
            durations = torch.where(real_mask, real_dur, torch.zeros_like(durations)).long()
        else:
            # When phoneme_lens is not explicitly provided, preserve zero-duration padding
            # while clamping real non-zero durations to >= 1 frame.
            is_nonzero = durations > 0
            durations = torch.where(is_nonzero, torch.clamp(durations, min=1), torch.zeros_like(durations)).long()

        cum_dur = torch.cumsum(durations, dim=-1)  # [B, T_phone]
        total_frames = torch.clamp(cum_dur[:, -1].max(), min=1)

        grid_t = torch.arange(total_frames, device=x.device).view(1, -1, 1)  # [1, T_frames, 1]
        cum_dur_prev = F.pad(cum_dur, (1, 0))[:, :-1].unsqueeze(1)          # [B, 1, T_phone]
        cum_dur_curr = cum_dur.unsqueeze(1)                                 # [B, 1, T_phone]

        mask = (grid_t >= cum_dur_prev) & (grid_t < cum_dur_curr)
        mask = mask.to(dtype=x.dtype)  # [B, T_frames, T_phone]

        out = torch.matmul(mask, x)  # [B, T_frames, D]
        return out


class VarianceAdaptor(nn.Module):
    """FastSpeech2-style Variance Adaptor for CAM-001."""

    def __init__(
        self,
        d_model: int = 192,
        contour_dim: int = 32,
        emphasis_dim: int = 16,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.d_model = d_model

        # Predictors
        self.duration_predictor = VariancePredictor(d_model=d_model, dropout=dropout)
        self.length_regulator = LengthRegulator()

        self.pitch_predictor = VariancePredictor(d_model=d_model, dropout=dropout)
        self.pitch_embedding = nn.Conv1d(1, d_model, kernel_size=9, padding=4)

        self.energy_predictor = VariancePredictor(d_model=d_model, dropout=dropout)
        self.energy_embedding = nn.Conv1d(1, d_model, kernel_size=9, padding=4)

        # Learned sequence-aligned conditionings
        self.pitch_contour_cond = LearnedPitchContourConditioning(
            num_contours=4,
            contour_dim=contour_dim,
            d_model=d_model,
        )
        self.emphasis_cond = LearnedEmphasisConditioning(
            num_emphasis=3,
            emphasis_dim=emphasis_dim,
            d_model=d_model,
        )

    def forward(
        self,
        encoder_output: torch.Tensor,             # [B, T_phone, d_model]
        pace: torch.Tensor,                       # [B] or [1] float
        pitch_contour_id: torch.Tensor,           # [B] or [1] int
        emphasis_id: torch.Tensor,                # [B] or [1] int
        target_durations: torch.Tensor | None = None,
        target_pitch: torch.Tensor | None = None,
        target_energy: torch.Tensor | None = None,
        phoneme_lens: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        """Variance adaptation forward pass.

        Returns:
            adapted_hidden: [B, T_frames, d_model]
            predicted_durations: [B, T_phone]
            log_dur_pred: [B, T_phone]
            predicted_pitch: [B, T_frames]
            predicted_energy: [B, T_frames]
        """
        B, T_phone, _ = encoder_output.shape

        # 1. Duration Prediction & Pace Control (PRD-028 §14)
        log_dur_pred = self.duration_predictor(encoder_output)
        durations = torch.clamp(torch.exp(log_dur_pred) - 1.0, min=1.0)

        # Apply pace duration scaling (pace > 1.0 -> faster -> shorter duration)
        pace_factor = pace.view(B, 1)
        durations = durations / torch.clamp(pace_factor, min=0.1)
        durations = torch.round(torch.clamp(durations, min=1.0)).long()

        if phoneme_lens is not None:
            phone_range = torch.arange(T_phone, device=encoder_output.device).view(1, -1)
            real_mask = phone_range < phoneme_lens.view(B, 1)
            durations = torch.where(real_mask, durations, torch.zeros_like(durations))

        if target_durations is not None:
            active_durations = target_durations
            if phoneme_lens is not None:
                phone_range = torch.arange(T_phone, device=encoder_output.device).view(1, -1)
                real_mask = phone_range < phoneme_lens.view(B, 1)
                active_durations = torch.where(real_mask, active_durations, torch.zeros_like(active_durations))
        else:
            active_durations = durations

        # 2. Length Regulation (Expand from phoneme to frame resolution)
        expanded_hidden = self.length_regulator(encoder_output, active_durations, phoneme_lens=phoneme_lens)
        T_exp = expanded_hidden.shape[1]

        # 3. Pitch Contour Modulation & Prediction (PRD-028 §15)
        contour_features = self.pitch_contour_cond(pitch_contour_id, expanded_hidden)
        pitch_input = expanded_hidden + contour_features
        pitch_pred = self.pitch_predictor(pitch_input)

        if target_pitch is not None:
            if target_pitch.shape[1] < T_exp:
                active_pitch = F.pad(target_pitch, (0, T_exp - target_pitch.shape[1]))
            else:
                active_pitch = target_pitch[:, :T_exp]
        else:
            active_pitch = pitch_pred

        pitch_emb = self.pitch_embedding(active_pitch.unsqueeze(1)).transpose(1, 2)

        # 4. Energy / Emphasis Modulation & Prediction (PRD-028 §16)
        emphasis_features = self.emphasis_cond(emphasis_id, expanded_hidden)
        energy_input = expanded_hidden + emphasis_features
        energy_pred = self.energy_predictor(energy_input)

        if target_energy is not None:
            if target_energy.shape[1] < T_exp:
                active_energy = F.pad(target_energy, (0, T_exp - target_energy.shape[1]))
            else:
                active_energy = target_energy[:, :T_exp]
        else:
            active_energy = energy_pred

        energy_emb = self.energy_embedding(active_energy.unsqueeze(1)).transpose(1, 2)

        # 5. Combine all variance features into final frame hidden states
        adapted_hidden = expanded_hidden + pitch_emb + energy_emb + contour_features + emphasis_features

        return adapted_hidden, durations, log_dur_pred, pitch_pred, energy_pred
