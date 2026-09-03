"""CAM-001 Text / Phoneme Encoder (PRD-028 §2, §17).

Consumes phoneme token sequences and produces contextual hidden representations.
Fully compatible with dynamic ONNX sequence length exports.
"""

from __future__ import annotations

import math
import torch
import torch.nn as nn
import torch.nn.functional as F


class PositionalEncoding(nn.Module):
    """Sinusoidal positional encoding with dynamic arbitrary sequence length support."""

    def __init__(self, d_model: int, max_len: int = 16384) -> None:
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer("pe", pe.unsqueeze(0))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: [B, T, D]
        seq_len = x.size(1)
        if seq_len > self.pe.size(1):
            position = torch.arange(0, seq_len, dtype=torch.float, device=x.device).unsqueeze(1)
            div_term = torch.exp(torch.arange(0, x.size(2), 2, device=x.device).float() * (-math.log(10000.0) / x.size(2)))
            pe = torch.zeros(seq_len, x.size(2), device=x.device)
            pe[:, 0::2] = torch.sin(position * div_term)
            pe[:, 1::2] = torch.cos(position * div_term)
            return x + pe.unsqueeze(0)
        return x + self.pe[:, :seq_len, :]


class DynamicMultiHeadAttention(nn.Module):
    """Multi-Head Attention supporting variable/dynamic sequence lengths in ONNX."""

    def __init__(self, d_model: int = 192, n_heads: int = 4, dropout: float = 0.1) -> None:
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.head_dim = d_model // n_heads

        self.q_proj = nn.Linear(d_model, d_model)
        self.k_proj = nn.Linear(d_model, d_model)
        self.v_proj = nn.Linear(d_model, d_model)
        self.out_proj = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, q: torch.Tensor, k: torch.Tensor, v: torch.Tensor, mask: torch.Tensor | None = None) -> torch.Tensor:
        B = q.shape[0]
        T_q = q.shape[1]
        T_k = k.shape[1]

        q = self.q_proj(q).view(B, T_q, self.n_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(k).view(B, T_k, self.n_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(v).view(B, T_k, self.n_heads, self.head_dim).transpose(1, 2)

        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.head_dim)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        attn = F.softmax(scores, dim=-1)
        attn = self.dropout(attn)

        context = torch.matmul(attn, v)  # [B, n_heads, T_q, head_dim]
        context = context.transpose(1, 2).contiguous().view(B, T_q, self.d_model)
        return self.out_proj(context)


class FFTBlock(nn.Module):
    """Feed-Forward Transformer block with dynamic Multi-Head Attention and Conv1D."""

    def __init__(
        self,
        d_model: int = 192,
        n_heads: int = 4,
        conv_filter_size: int = 768,
        conv_kernel_size: int = 5,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.slf_attn = DynamicMultiHeadAttention(
            d_model=d_model,
            n_heads=n_heads,
            dropout=dropout,
        )
        self.norm1 = nn.LayerNorm(d_model)
        self.dropout1 = nn.Dropout(dropout)

        padding = (conv_kernel_size - 1) // 2
        self.conv1 = nn.Conv1d(d_model, conv_filter_size, kernel_size=conv_kernel_size, padding=padding)
        self.conv2 = nn.Conv1d(conv_filter_size, d_model, kernel_size=conv_kernel_size, padding=padding)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout2 = nn.Dropout(dropout)

    def forward(self, x: torch.Tensor, mask: torch.Tensor | None = None) -> torch.Tensor:
        # Self-attention
        res = x
        attn_out = self.slf_attn(x, x, x, mask=mask)
        x = self.norm1(res + self.dropout1(attn_out))

        # 1D Convolutional feed-forward
        res = x
        conv_in = x.transpose(1, 2)
        h = F.relu(self.conv1(conv_in))
        h = self.conv2(h)
        conv_out = h.transpose(1, 2)
        x = self.norm2(res + self.dropout2(conv_out))
        return x


class PhonemeEncoder(nn.Module):
    """Phoneme sequence encoder for CAM-001."""

    def __init__(
        self,
        vocab_size: int = 256,
        d_model: int = 192,
        num_layers: int = 4,
        num_heads: int = 4,
        conv_filter_size: int = 768,
        conv_kernel_size: int = 5,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
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
        self.d_model = d_model

    def forward(self, phoneme_ids: torch.Tensor, mask: torch.Tensor | None = None) -> torch.Tensor:
        """Encode phoneme IDs into contextual hidden states [B, T_phone, d_model]."""
        x = self.embedding(phoneme_ids) * math.sqrt(self.d_model)
        x = self.pos_enc(x)
        for layer in self.layers:
            x = layer(x, mask=mask)
        return self.layer_norm(x)
