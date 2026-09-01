"""Claire Acoustic Model (CAM-001) Package (PRD-028)."""

from cse.acoustic.cam.acoustic_model import CamAcousticModel
from cse.acoustic.cam.adapter import CAMConditioningTensors, GraphToConditioningAdapter
from cse.acoustic.cam.backend import CAMBackend
from cse.acoustic.cam.benchmark import run_full_cam_benchmark
from cse.acoustic.cam.config import (
    CAMConfig,
    EXPRESSO_READ_STYLES,
    EXPRESSO_SPEAKERS,
    PITCH_CONTOURS,
    PRIMARY_INTENTS,
)
from cse.acoustic.cam.downloader import resolve_cam_model_paths
from cse.acoustic.cam.onnx_export import (
    export_cam_acoustic_onnx,
    export_cam_vocoder_onnx,
    get_model_size_mb,
    quantize_cam_onnx,
    validate_onnx_inference,
)
from cse.acoustic.cam.phonemizer import CAMPhonemizer
from cse.acoustic.cam.preprocessor import ExpressoDatasetPreprocessor
from cse.acoustic.cam.vocoder import CamVocoder

__all__ = [
    "CAMConfig",
    "CAMPhonemizer",
    "GraphToConditioningAdapter",
    "CAMConditioningTensors",
    "CamAcousticModel",
    "CamVocoder",
    "CAMBackend",
    "ExpressoDatasetPreprocessor",
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
