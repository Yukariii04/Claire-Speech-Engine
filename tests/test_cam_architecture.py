"""Tests for CAM-001 Acoustic and Vocoder Architecture (PRD-028 §2, §7-16, §18, §20)."""

import pytest
import torch

from cse.acoustic.cam.acoustic_model import CamAcousticModel
from cse.acoustic.cam.config import CAMConfig
from cse.acoustic.cam.modules.conditioning import (
    LearnedEmphasisConditioning,
    LearnedPitchContourConditioning,
    PrimaryIntentEmbedding,
    SpeakerEmbedding,
    SpeakerStyleMixer,
    StyleEmbedding,
)
from cse.acoustic.cam.modules.decoder import AcousticDecoder
from cse.acoustic.cam.modules.encoder import PhonemeEncoder
from cse.acoustic.cam.modules.variance_adaptor import LengthRegulator, VarianceAdaptor
from cse.acoustic.cam.vocoder import CamVocoder


@pytest.fixture
def config():
    return CAMConfig()


@pytest.fixture
def acoustic_model(config):
    return CamAcousticModel(config).eval()


@pytest.fixture
def vocoder():
    return CamVocoder().eval()


class TestCAMArchitecture:
    def test_style_embedding_dimension_is_128(self):
        style_mod = StyleEmbedding(num_styles=8, style_dim=128)
        assert style_mod.style_dim == 128
        out = style_mod(style_id=torch.tensor([0, 7], dtype=torch.long))
        assert out.shape == (2, 128)

    def test_speaker_embedding_dimension_is_64(self):
        spk_mod = SpeakerEmbedding(num_speakers=16, speaker_dim=64)
        assert spk_mod.speaker_dim == 64
        out = spk_mod(speaker_id=torch.tensor([0, 1], dtype=torch.long))
        assert out.shape == (2, 64)

    def test_speaker_style_mixer_output_shape(self, config):
        mixer = SpeakerStyleMixer(speaker_dim=64, style_dim=128, d_model=config.d_model)
        spk_emb = torch.randn(2, 64)
        style_emb = torch.randn(2, 128)
        mixed = mixer(spk_emb, style_emb)
        assert mixed.shape == (2, config.d_model)

    def test_primary_intent_is_separate_and_broadcast(self, config):
        intent_mod = PrimaryIntentEmbedding(num_intents=4, intent_dim=32, d_model=config.d_model)
        assert intent_mod.intent_dim == 32
        out = intent_mod(intent_id=torch.tensor([0, 1]), seq_len=15)
        # Sequence-broadcast shape [2, 15, d_model]
        assert out.shape == (2, 15, config.d_model)

    def test_pitch_contour_learned_conditioning(self, config):
        contour_mod = LearnedPitchContourConditioning(num_contours=4, contour_dim=32, d_model=config.d_model)
        hidden = torch.randn(2, 20, config.d_model)
        out = contour_mod(contour_id=torch.tensor([0, 1]), hidden=hidden)
        assert out.shape == (2, 20, config.d_model)

    def test_emphasis_learned_conditioning(self, config):
        emphasis_mod = LearnedEmphasisConditioning(num_emphasis=3, emphasis_dim=16, d_model=config.d_model)
        hidden = torch.randn(2, 20, config.d_model)
        out = emphasis_mod(emphasis_id=torch.tensor([0, 1]), hidden=hidden)
        assert out.shape == (2, 20, config.d_model)

    def test_length_regulator_dynamic_expansion(self):
        lr = LengthRegulator()
        x = torch.randn(1, 5, 192)
        durations = torch.tensor([[2, 1, 3, 2, 1]], dtype=torch.long)
        expanded = lr(x, durations)
        assert expanded.shape == (1, 9, 192)

    def test_phoneme_encoder_forward(self, config):
        enc = PhonemeEncoder(vocab_size=256, d_model=config.d_model, num_layers=2)
        phone_ids = torch.randint(0, 256, (2, 12))
        hidden = enc(phone_ids)
        assert hidden.shape == (2, 12, config.d_model)

    def test_acoustic_model_end_to_end_forward(self, acoustic_model):
        phone_ids = torch.tensor([[2, 15, 30, 45, 60, 3]], dtype=torch.long)
        spk_id = torch.tensor([0], dtype=torch.long)
        style_id = torch.tensor([1], dtype=torch.long)
        intent_id = torch.tensor([0], dtype=torch.long)
        pace = torch.tensor([1.0], dtype=torch.float32)
        contour_id = torch.tensor([0], dtype=torch.long)
        emphasis_id = torch.tensor([0], dtype=torch.long)

        mel, dur = acoustic_model(
            phoneme_ids=phone_ids,
            speaker_id=spk_id,
            style_id=style_id,
            intent_id=intent_id,
            pace=pace,
            pitch_contour_id=contour_id,
            emphasis_id=emphasis_id,
        )

        assert mel.ndim == 3
        assert mel.shape[0] == 1
        assert mel.shape[2] == 80
        assert mel.shape[1] == int(dur.sum())
        assert dur.shape == (1, 6)

    def test_vocoder_forward_24khz(self, vocoder):
        # 50 frames of 80-channel mel
        mel = torch.randn(1, 50, 80)
        audio = vocoder(mel)
        # Hop length = 256 -> 50 * 256 = 12800 samples (at 24 kHz = 0.533 seconds)
        assert audio.ndim == 3
        assert audio.shape == (1, 1, 50 * 256)
        assert torch.all(audio >= -1.0) and torch.all(audio <= 1.0)

    def test_parameter_counts(self, acoustic_model, vocoder):
        ac_params = acoustic_model.count_parameters()
        voc_params = vocoder.count_parameters()
        total_params = ac_params + voc_params
        # Typical FastSpeech2 + MRF Vocoder has ~10M - 35M parameters (< 100MB)
        assert ac_params > 0
        assert voc_params > 0
        assert total_params < 50_000_000
