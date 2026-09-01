"""CAM-001 Learned Conditioning Modules (PRD-028 §7, §8, §9, §10, §11, §12, §15, §16).

Implements:
- 128-d continuous Style Embedding table (PRD-028 §7)
- 64-d Speaker Embedding table (PRD-028 §8)
- Lightweight learned Speaker+Style Mixer (PRD-028 §11)
- 32-d Primary Intent Embedding table (PRD-028 §12) - strictly separate from speaker/style
- 32-d Learned Pitch Contour representation (PRD-028 §15) - sequence aligned
- 16-d Learned Emphasis representation (PRD-028 §16)
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class StyleEmbedding(nn.Module):
    """Discrete learned embedding table for 8 Expresso styles (PRD-028 §7).

    Exposes a fixed 128-dimensional continuous interface.
    """

    def __init__(self, num_styles: int = 8, style_dim: int = 128) -> None:
        super().__init__()
        self.num_styles = num_styles
        self.style_dim = style_dim
        self.embedding = nn.Embedding(num_styles, style_dim)
        nn.init.normal_(self.embedding.weight, mean=0.0, std=0.1)

    def forward(
        self,
        style_id: torch.Tensor | None = None,
        style_vector: torch.Tensor | None = None,
    ) -> torch.Tensor:
        """Return a continuous [B, 128] style embedding tensor.

        Accepts either discrete style_id [B] or continuous style_vector [B, 128].
        """
        if style_vector is not None:
            return style_vector
        if style_id is not None:
            return self.embedding(style_id)
        # Default style ID 0
        device = next(self.parameters()).device
        return self.embedding(torch.zeros(1, dtype=torch.long, device=device))


class SpeakerEmbedding(nn.Module):
    """Learned discrete embedding table for speaker identity (PRD-028 §8).

    Kept separate from style. Selected practical dimension = 64.
    """

    def __init__(self, num_speakers: int = 16, speaker_dim: int = 64) -> None:
        super().__init__()
        self.num_speakers = num_speakers
        self.speaker_dim = speaker_dim
        self.embedding = nn.Embedding(num_speakers, speaker_dim)
        nn.init.normal_(self.embedding.weight, mean=0.0, std=0.1)

    def forward(self, speaker_id: torch.Tensor) -> torch.Tensor:
        """Return [B, 64] speaker embedding tensor."""
        return self.embedding(speaker_id)


class SpeakerStyleMixer(nn.Module):
    """Lightweight learned mixer combining speaker and style embeddings (PRD-028 §11).

    speaker (64) + style (128) -> [B, d_model]
    Primary intent is NOT routed through here.
    """

    def __init__(self, speaker_dim: int = 64, style_dim: int = 128, d_model: int = 192) -> None:
        super().__init__()
        self.fc1 = nn.Linear(speaker_dim + style_dim, d_model)
        self.act = nn.SiLU()
        self.fc2 = nn.Linear(d_model, d_model)
        self.layer_norm = nn.LayerNorm(d_model)

    def forward(self, speaker_emb: torch.Tensor, style_emb: torch.Tensor) -> torch.Tensor:
        """Mix speaker and style embeddings into a combined conditioning vector [B, d_model]."""
        cat = torch.cat([speaker_emb, style_emb], dim=-1)
        x = self.fc1(cat)
        x = self.act(x)
        x = self.fc2(x)
        return self.layer_norm(x)


class PrimaryIntentEmbedding(nn.Module):
    """Learned intent embedding for communicative intent (PRD-028 §12).

    Categories: statement, question, exclamation (and reserved).
    Selected practical dimension = 32.
    Strictly separate from speaker and style identity.
    Broadcast across phoneme sequence.
    """

    def __init__(self, num_intents: int = 4, intent_dim: int = 32, d_model: int = 192) -> None:
        super().__init__()
        self.num_intents = num_intents
        self.intent_dim = intent_dim
        self.embedding = nn.Embedding(num_intents, intent_dim)
        self.proj = nn.Linear(intent_dim, d_model)
        nn.init.normal_(self.embedding.weight, mean=0.0, std=0.1)

    def forward(self, intent_id: torch.Tensor, seq_len: int | torch.Tensor) -> torch.Tensor:
        """Return sequence-broadcast intent conditioning [B, seq_len, d_model]."""
        emb = self.embedding(intent_id)  # [B, 32]
        proj = self.proj(emb)            # [B, d_model]
        # Broadcast across sequence dimension [B, seq_len, d_model]
        if isinstance(seq_len, int):
            return proj.unsqueeze(1).expand(-1, seq_len, -1)
        else:
            return proj.unsqueeze(1).repeat(1, seq_len, 1)


class LearnedPitchContourConditioning(nn.Module):
    """Sequence-aligned learned pitch contour conditioning (PRD-028 §15).

    Maps categorical CPE instruction (flat, rising, falling, peaked) into
    learned contour representation across normalized phoneme positions.
    NO hard-coded DSP sigmoid/linear curves.
    """

    def __init__(self, num_contours: int = 4, contour_dim: int = 32, d_model: int = 192) -> None:
        super().__init__()
        self.contour_emb = nn.Embedding(num_contours, contour_dim)
        self.pos_proj = nn.Linear(1 + contour_dim, d_model)
        self.act = nn.GELU()
        self.out_proj = nn.Linear(d_model, d_model)

    def forward(self, contour_id: torch.Tensor, hidden: torch.Tensor) -> torch.Tensor:
        """Generate sequence-aligned learned contour tensor matching hidden shape [B, T, d_model]."""
        B, T, _ = hidden.shape
        c_emb = self.contour_emb(contour_id)  # [B, contour_dim]
        c_emb_expanded = c_emb.unsqueeze(1).expand(B, T, -1)

        # Dynamic normalized position [0.0 ... 1.0] in ONNX
        t_range = torch.arange(T, device=hidden.device, dtype=hidden.dtype)
        denom = torch.clamp(torch.tensor(1.0, device=hidden.device, dtype=hidden.dtype) * (T - 1), min=1.0)
        pos = (t_range / denom).view(1, -1, 1).expand(B, -1, 1)

        features = torch.cat([pos, c_emb_expanded], dim=-1)  # [B, T, 1 + contour_dim]
        h = self.pos_proj(features)
        h = self.act(h)
        return self.out_proj(h)


class LearnedEmphasisConditioning(nn.Module):
    """Sequence-aligned learned emphasis conditioning (PRD-028 §16).

    Interprets whole-utterance CPE categories: none, final_word, throughout.
    """

    def __init__(self, num_emphasis: int = 3, emphasis_dim: int = 16, d_model: int = 192) -> None:
        super().__init__()
        self.emphasis_emb = nn.Embedding(num_emphasis, emphasis_dim)
        self.proj = nn.Linear(emphasis_dim + 1, d_model)
        self.act = nn.GELU()

    def forward(self, emphasis_id: torch.Tensor, hidden: torch.Tensor) -> torch.Tensor:
        """Generate sequence-aligned emphasis tensor matching hidden shape [B, T, d_model]."""
        B, T, _ = hidden.shape
        e_emb = self.emphasis_emb(emphasis_id)  # [B, emphasis_dim]
        e_emb_expanded = e_emb.unsqueeze(1).expand(B, T, -1)

        t_range = torch.arange(T, device=hidden.device, dtype=hidden.dtype)
        denom = torch.clamp(torch.tensor(1.0, device=hidden.device, dtype=hidden.dtype) * (T - 1), min=1.0)
        pos = (t_range / denom).view(1, -1, 1).expand(B, -1, 1)

        features = torch.cat([pos, e_emb_expanded], dim=-1)
        return self.act(self.proj(features))
