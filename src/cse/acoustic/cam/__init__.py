"""Claire Acoustic Model (CAM-001) Package (PRD-028)."""

from cse.acoustic.cam.adapter import CAMConditioningTensors, GraphToConditioningAdapter
from cse.acoustic.cam.config import (
    CAMConfig,
    EXPRESSO_READ_STYLES,
    EXPRESSO_SPEAKERS,
    PITCH_CONTOURS,
    PRIMARY_INTENTS,
)
from cse.acoustic.cam.downloader import resolve_cam_model_paths
from cse.acoustic.cam.phonemizer import CAMPhonemizer

# Lazy-load PyTorch models, runtime backend, and ONNX export tools to keep runtime/import dependency-light
_LAZY_IMPORTS = {
    "CAMBackend": ("cse.acoustic.cam.backend", "CAMBackend"),
    "CamAcousticModel": ("cse.acoustic.cam.acoustic_model", "CamAcousticModel"),
    "CamVocoder": ("cse.acoustic.cam.vocoder", "CamVocoder"),
    "compute_mel_spectrogram": ("cse.acoustic.cam.preprocessor", "compute_mel_spectrogram"),
    "resample_audio": ("cse.acoustic.cam.preprocessor", "resample_audio"),
    "export_cam_acoustic_onnx": ("cse.acoustic.cam.onnx_export", "export_cam_acoustic_onnx"),
    "export_cam_vocoder_onnx": ("cse.acoustic.cam.onnx_export", "export_cam_vocoder_onnx"),
    "quantize_cam_onnx": ("cse.acoustic.cam.onnx_export", "quantize_cam_onnx"),
    "get_model_size_mb": ("cse.acoustic.cam.onnx_export", "get_model_size_mb"),
    "validate_onnx_inference": ("cse.acoustic.cam.onnx_export", "validate_onnx_inference"),
    "run_full_cam_benchmark": ("cse.acoustic.cam.benchmark", "run_full_cam_benchmark"),
}


def __getattr__(name: str):
    if name in _LAZY_IMPORTS:
        import importlib
        mod_name, attr_name = _LAZY_IMPORTS[name]
        mod = importlib.import_module(mod_name)
        val = getattr(mod, attr_name)
        globals()[name] = val
        return val
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return list(__all__)

__all__ = [
    "CAMConfig",
    "CAMPhonemizer",
    "GraphToConditioningAdapter",
    "CAMConditioningTensors",
    "CamAcousticModel",
    "CamVocoder",
    "CAMBackend",
    "compute_mel_spectrogram",
    "resample_audio",
    "export_cam_acoustic_onnx",
    "export_cam_vocoder_onnx",
    "quantize_cam_onnx",
    "get_model_size_mb",
    "validate_onnx_inference",
    "resolve_cam_model_paths",
    "run_full_cam_benchmark",
    "EXPRESSO_READ_STYLES",
    "EXPRESSO_SPEAKERS",
    "PRIMARY_INTENTS",
    "PITCH_CONTOURS",
]
