"""Capabilities for StyleTTS2."""
from cse.acoustic.backend.capabilities import BackendCapabilities

def get_styletts2_capabilities() -> BackendCapabilities:
    return BackendCapabilities(
        backend_name="styletts2",
        supports_streaming=False,
        supports_batch=False,
        supports_multispeaker=False,
        supports_voice_cloning=True,
        emotion="medium",
        sample_rate=24000,
        requires_gpu=True,
        supported_languages=("en",),
        backend_version="1.0.0"
    )
