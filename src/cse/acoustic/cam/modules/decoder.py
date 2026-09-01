"""CAM-001 Acoustic Decoder Trunk (PRD-028 §2, §13).

Consumes adapted frame hidden representations and generates 80-channel
mel-spectrogram acoustic features.
"""

from __future__ import annotations

import torch
import torch.nn as nn
from cse.acoustic.cam.modules.encoder import FFTBlock, PositionalEncoding


class AcousticDecoder(nn.Module):
    """Non-autoregressive frame decoder producing 80-channel mel-spectrogram."""

    def __init__(
        self,
        d_model: int = 192,
        n_mels: int = 80,
        num_layers: int = 4,
        num_heads: int = 4,
        conv_filter_size: int = 768,
        conv_kernel_size: int = 5,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.pos_enc = PositionalEncoding(d_model)
        self.layers = nn.ModuleList([
            FFTBlock(
                d_model=d_model,
                n_heads=num_heads,
                conv_filter_size=conv_filter_size,
                conv_kernel_size=conv_kernel_size,
                dropout=dropout,
            )
            for _ in range(num_layers)
        ])
        self.layer_norm = nn.LayerNorm(d_model)
        self.mel_linear = nn.Linear(d_model, n_mels)

    def forward(self, x: torch.Tensor, mask: torch.Tensor | None = None) -> torch.Tensor:
        """Decode frame representations into mel-spectrogram [B, T_frames, n_mels]."""
        x = self.pos_enc(x)
        for layer in self.layers:
            x = layer(x, mask=mask)
        x = self.layer_norm(x)
        mel = self.mel_linear(x)
        return mel
