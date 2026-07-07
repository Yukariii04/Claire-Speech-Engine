"""Capabilities for Fish Speech."""
from cse.acoustic.backend.capabilities import BackendCapabilities

def get_fishspeech_capabilities() -> BackendCapabilities:
    return BackendCapabilities(
        backend_name="fishspeech",
        supports_streaming=False,
        supports_batch=False,
        supports_multispeaker=False,
        supports_voice_cloning=True,
        emotion="high",
        sample_rate=44100,
        requires_gpu=True,
        supported_languages=("en",),
        backend_version="1.0.0"
    )
