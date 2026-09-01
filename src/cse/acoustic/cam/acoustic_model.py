"""CAM-001 Acoustic Model (PRD-028 §2, §3, §7-16, §18, §19).

Integrates:
- Phoneme Encoder
- 128-d Style Embedding & 64-d Speaker Embedding with lightweight Learned Mixer
- 32-d Primary Intent Embedding broadcast across sequence
- FastSpeech2-style Variance Adaptor (Duration, Length Regulator, Pitch, Energy)
- Frame-level Non-Autoregressive Acoustic Decoder
"""

from __future__ import annotations

import torch
import torch.nn as nn

from cse.acoustic.cam.config import CAMConfig
from cse.acoustic.cam.modules.conditioning import (
    PrimaryIntentEmbedding,
    SpeakerEmbedding,
    SpeakerStyleMixer,
    StyleEmbedding,
)
from cse.acoustic.cam.modules.decoder import AcousticDecoder
from cse.acoustic.cam.modules.encoder import PhonemeEncoder
from cse.acoustic.cam.modules.variance_adaptor import VarianceAdaptor


class CamAcousticModel(nn.Module):
    """The Claire Acoustic Model (CAM-001) Trunk."""

    def __init__(self, config: CAMConfig | None = None) -> None:
        super().__init__()
        self.config = config or CAMConfig()

        d_model = self.config.d_model

        # 1. Phoneme Encoder
        self.encoder = PhonemeEncoder(
            vocab_size=self.config.vocab_size,
            d_model=d_model,
            num_layers=self.config.encoder_layers,
            num_heads=self.config.encoder_heads,
            conv_filter_size=self.config.conv_filter_size,
            conv_kernel_size=self.config.conv_kernel_size,
            dropout=self.config.dropout,
        )

        # 2. Conditioning modules
        self.style_embedding = StyleEmbedding(
            num_styles=8,
            style_dim=self.config.style_dim,  # 128
        )
        self.speaker_embedding = SpeakerEmbedding(
            num_speakers=16,
            speaker_dim=self.config.speaker_dim,  # 64
        )
        self.speaker_style_mixer = SpeakerStyleMixer(
            speaker_dim=self.config.speaker_dim,  # 64
            style_dim=self.config.style_dim,      # 128
            d_model=d_model,
        )
        # Primary intent is strictly separate from speaker/style mixer
        self.intent_embedding = PrimaryIntentEmbedding(
            num_intents=4,
            intent_dim=self.config.intent_dim,  # 32
            d_model=d_model,
        )

        # 3. Variance Adaptor
        self.variance_adaptor = VarianceAdaptor(
            d_model=d_model,
            contour_dim=self.config.contour_dim,
            emphasis_dim=self.config.emphasis_dim,
            dropout=self.config.dropout,
        )

        # 4. Acoustic Decoder
        self.decoder = AcousticDecoder(
            d_model=d_model,
            n_mels=self.config.n_mels,
            num_layers=self.config.decoder_layers,
            num_heads=self.config.decoder_heads,
            conv_filter_size=self.config.conv_filter_size,
            conv_kernel_size=self.config.conv_kernel_size,
            dropout=self.config.dropout,
        )

    def forward(
        self,
        phoneme_ids: torch.Tensor,                # [B, T_phone] int64
        speaker_id: torch.Tensor,                 # [B] int64
        style_id: torch.Tensor,                   # [B] int64
        intent_id: torch.Tensor,                  # [B] int64
        pace: torch.Tensor,                       # [B] float32
        pitch_contour_id: torch.Tensor,           # [B] int64
        emphasis_id: torch.Tensor,                # [B] int64
        style_vector: torch.Tensor | None = None, # [B, 128] float32 (optional)
        target_durations: torch.Tensor | None = None,
        target_pitch: torch.Tensor | None = None,
        target_energy: torch.Tensor | None = None,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Acoustic forward pass producing mel-spectrogram features and durations.

        Returns:
            mel_output: [B, T_frames, n_mels] (e.g. [1, T_frames, 80])
            durations: [B, T_phone] (predicted phoneme durations)
        """
        B, T_phone = phoneme_ids.shape

        # 1. Encode phonemes
        enc_out = self.encoder(phoneme_ids)  # [B, T_phone, d_model]

        # 2. Extract Speaker & Style Embeddings and mix through lightweight mixer
        style_emb = self.style_embedding(style_id=style_id, style_vector=style_vector)  # [B, 128]
        speaker_emb = self.speaker_embedding(speaker_id)                                # [B, 64]
        spk_style_cond = self.speaker_style_mixer(speaker_emb, style_emb)               # [B, d_model]

        # 3. Extract Primary Intent Embedding (broadcast across sequence)
        intent_cond = self.intent_embedding(intent_id, seq_len=T_phone)                # [B, T_phone, d_model]

        # 4. Inject conditioning into phoneme representations
        # Speaker+Style broadcast + Intent sequence representation
        h = enc_out + spk_style_cond.unsqueeze(1) + intent_cond

        # 5. Variance Adaptation (Duration, Length Regulation, Pitch Contour, Emphasis)
        adapted_hidden, durations, pitch_pred, energy_pred = self.variance_adaptor(
            encoder_output=h,
            pace=pace,
            pitch_contour_id=pitch_contour_id,
            emphasis_id=emphasis_id,
            target_durations=target_durations,
            target_pitch=target_pitch,
            target_energy=target_energy,
        )

        # 6. Decode into 80-channel mel-spectrogram
        mel_output = self.decoder(adapted_hidden)  # [B, T_frames, 80]

        return mel_output, durations

    def count_parameters(self) -> int:
        """Count total trainable parameters."""
        return sum(p.numel() for p in self.parameters() if p.requires_grad)
