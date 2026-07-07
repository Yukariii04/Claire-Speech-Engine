"""Exceptions for StyleTTS2."""
from cse.acoustic.backend.exceptions import BackendError

class StyleTTS2InitializationError(BackendError): pass
class SpeechGenerationError(BackendError): pass
