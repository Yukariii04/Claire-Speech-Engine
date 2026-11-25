"""SpeechResult for KittenTTS and acoustic backends.

This module re-exports SpeechResult from the canonical location
(cse.acoustic.backend.result) for backward compatibility.
"""

from __future__ import annotations

from cse.acoustic.backend.result import SpeechResult

__all__ = ["SpeechResult"]
