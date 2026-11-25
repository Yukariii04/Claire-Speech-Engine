"""Tests for CAM-001 Audio Preprocessor Utilities (PRD-028 §4, §5)."""

import numpy as np

from cse.acoustic.cam.preprocessor import (
    compute_mel_spectrogram,
    resample_audio,
)


class TestCAMPreprocessor:
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
        mel = compute_mel_spectrogram(audio, sample_rate=24000, n_mels=100, hop_length=256)
        assert mel.ndim == 2
        assert mel.shape[1] == 100
        # Expected frames ~ 12000 // 256 + 1 = 47
        assert abs(mel.shape[0] - 47) <= 2
