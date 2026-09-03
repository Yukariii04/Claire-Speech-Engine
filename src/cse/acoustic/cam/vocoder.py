"""CAM-001 Lightweight Neural Vocoder (PRD-028 §2, §4, §18, §20).

Lightweight neural vocoder converting 100-channel mel-spectrograms into 24 kHz audio.
Supports dynamic/variable frame length inputs with seamless ONNX export.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from cse.acoustic.cam.config import CAMConfig


class MRFBlock(nn.Module):
    """Multi-Receptive Field ResNet Block."""

    def __init__(self, channels: int, kernel_size: int = 3, dilations: tuple[int, ...] = (1, 3, 5)) -> None:
        super().__init__()
        self.convs1 = nn.ModuleList()
        self.convs2 = nn.ModuleList()

        for d in dilations:
            pad1 = (kernel_size - 1) * d // 2
            self.convs1.append(
                nn.Conv1d(channels, channels, kernel_size=kernel_size, dilation=d, padding=pad1)
            )
            pad2 = (kernel_size - 1) // 2
            self.convs2.append(
                nn.Conv1d(channels, channels, kernel_size=kernel_size, dilation=1, padding=pad2)
            )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        for c1, c2 in zip(self.convs1, self.convs2):
            xt = F.leaky_relu(x, 0.1)
            xt = c1(xt)
            xt = F.leaky_relu(xt, 0.1)
            xt = c2(xt)
            x = x + xt
        return x


class CamVocoder(nn.Module):
    """Lightweight 24 kHz Neural Vocoder for CAM-001 (Vocos-compatible 100 mels)."""

    def __init__(
        self,
        n_mels: int = 100,
        upsample_initial_channel: int = 256,
        upsample_rates: tuple[int, ...] = (8, 8, 2, 2),  # Product = 256 (hop_length)
        upsample_kernel_sizes: tuple[int, ...] = (16, 16, 4, 4),
        resblock_kernel_sizes: tuple[int, ...] = (3, 7, 11),
        resblock_dilation_sizes: tuple[tuple[int, ...], ...] = ((1, 3, 5), (1, 3, 5), (1, 3, 5)),
    ) -> None:
        super().__init__()
        self.n_mels = n_mels
        self.hop_length = 256  # 8 * 8 * 2 * 2

        # Initial projection
        self.conv_pre = nn.Conv1d(n_mels, upsample_initial_channel, kernel_size=7, stride=1, padding=3)

        # Upsampling stages
        self.ups = nn.ModuleList()
        curr_channel = upsample_initial_channel
        for u_rate, u_k in zip(upsample_rates, upsample_kernel_sizes):
            next_channel = curr_channel // 2
            self.ups.append(
                nn.ConvTranspose1d(
                    curr_channel,
                    next_channel,
                    kernel_size=u_k,
                    stride=u_rate,
                    padding=(u_k - u_rate) // 2,
                )
            )
            curr_channel = next_channel

        # Multi-Receptive Field ResBlocks per upsample stage
        self.resblocks = nn.ModuleList()
        curr_channel = upsample_initial_channel
        for _ in upsample_rates:
            curr_channel //= 2
            for k, d in zip(resblock_kernel_sizes, resblock_dilation_sizes):
                self.resblocks.append(MRFBlock(channels=curr_channel, kernel_size=k, dilations=d))

        self.num_mrf_per_stage = len(resblock_kernel_sizes)

        # Output projection
        self.conv_post = nn.Conv1d(curr_channel, 1, kernel_size=7, stride=1, padding=3)

    def forward(self, mel: torch.Tensor) -> torch.Tensor:
        """Synthesize 24 kHz audio waveform from 100-channel mel-spectrogram.

        Args:
            mel: [B, T_frames, 100] or [B, 100, T_frames] float tensor.

        Returns:
            waveform: [B, 1, T_samples] at 24 kHz (where T_samples = T_frames * 256).
        """
        # Standard input from acoustic model / ONNX: [B, T_frames, 100]
        # Transpose to [B, 100, T_frames] for 1D convolutions
        x = mel.transpose(1, 2)

        x = self.conv_pre(x)

        for i, up in enumerate(self.ups):
            x = F.leaky_relu(x, 0.1)
            x = up(x)
            xs: torch.Tensor | None = None
            for j in range(self.num_mrf_per_stage):
                idx = i * self.num_mrf_per_stage + j
                res_out = self.resblocks[idx](x)
                if xs is None:
                    xs = res_out
                else:
                    xs = xs + res_out
            x = xs / self.num_mrf_per_stage

        x = F.leaky_relu(x, 0.1)
        x = self.conv_post(x)
        x = torch.tanh(x)
        return x

    def count_parameters(self) -> int:
        """Count total trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
