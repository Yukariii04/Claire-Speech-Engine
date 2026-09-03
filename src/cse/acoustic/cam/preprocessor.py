"""CAM-001 Audio & Mel-Spectrogram Utilities (PRD-028 §4, PRD-029 §7).

Provides shared deterministic signal processing utilities:
- 24 kHz audio resampling
- 100-channel mel-spectrogram target computation
"""

from __future__ import annotations

import numpy as np


def resample_audio(
    audio: np.ndarray,
    orig_sr: int,
    target_sr: int = 24000,
) -> np.ndarray:
    """Resample 1D audio array to target sample rate (24 kHz) deterministically."""
    if orig_sr == target_sr:
        return audio.astype(np.float32)

    # Deterministic linear interpolation resampling
    num_orig_samples = len(audio)
    num_target_samples = int(round(num_orig_samples * float(target_sr) / float(orig_sr)))
    orig_indices = np.linspace(0, num_orig_samples - 1, num_target_samples)
    resampled = np.interp(orig_indices, np.arange(num_orig_samples), audio)
    return resampled.astype(np.float32)


def compute_mel_spectrogram(
    audio: np.ndarray,
    sample_rate: int = 24000,
    n_fft: int = 1024,
    hop_length: int = 256,
    win_length: int = 1024,
    n_mels: int = 100,
    f_min: float = 0.0,
    f_max: float = 12000.0,
) -> np.ndarray:
    """Compute 100-channel mel-spectrogram targets at 24 kHz deterministically."""
    # Create Hann window
    window = np.hanning(win_length)

    # Pad audio
    pad_len = n_fft // 2
    padded = np.pad(audio, (pad_len, pad_len), mode="reflect")

    # STFT calculation
    num_frames = max(1, (len(padded) - n_fft) // hop_length + 1)
    stft = np.zeros((num_frames, n_fft // 2 + 1), dtype=np.complex64)

    for t in range(num_frames):
        start = t * hop_length
        frame = padded[start : start + n_fft] * window
        spectrum = np.fft.rfft(frame, n=n_fft)
        stft[t] = spectrum

    magnitudes = np.abs(stft)  # [num_frames, n_fft // 2 + 1]

    # Mel filterbank construction
    mel_min = 2595.0 * np.log10(1.0 + f_min / 700.0)
    mel_max = 2595.0 * np.log10(1.0 + f_max / 700.0)
    mel_points = np.linspace(mel_min, mel_max, n_mels + 2)
    hz_points = 700.0 * (10.0 ** (mel_points / 2595.0) - 1.0)
    bins = np.floor((n_fft + 1) * hz_points / sample_rate).astype(int)

    fbank = np.zeros((n_mels, n_fft // 2 + 1), dtype=np.float32)
    for m in range(1, n_mels + 1):
        f_m_minus = bins[m - 1]
        f_m = bins[m]
        f_m_plus = bins[m + 1]

        for k in range(f_m_minus, f_m):
            if f_m != f_m_minus:
                fbank[m - 1, k] = (k - bins[m - 1]) / (bins[m] - bins[m - 1])
        for k in range(f_m, f_m_plus):
            if f_m_plus != f_m:
                fbank[m - 1, k] = (bins[m + 1] - k) / (bins[m + 1] - bins[m])

    # Apply filterbank
    mel_spec = np.dot(magnitudes, fbank.T)  # [num_frames, n_mels]
    mel_spec = np.log(np.clip(mel_spec, a_min=1e-5, a_max=None))

    return mel_spec.astype(np.float32)

