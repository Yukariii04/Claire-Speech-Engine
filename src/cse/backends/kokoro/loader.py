"""Kokoro Voice Loader (PRD-008 §8)."""

from __future__ import annotations

from cse.backends.kokoro.exceptions import VoiceLoadError


def resolve_voice(voice_name: str | None, default_voice: str) -> str:
    """Resolve a voice name to a Kokoro voice identifier.

    Args:
        voice_name: The requested voice name (e.g. 'af_sarah').
        default_voice: Fallback voice if none provided.

    Returns:
        The resolved Kokoro voice string.

    Raises:
        VoiceLoadError: If the voice name is empty after resolution.
    """
    resolved = voice_name or default_voice

    if not resolved or not resolved.strip():
        raise VoiceLoadError("No voice specified and no default voice configured.")

    return resolved.strip()
