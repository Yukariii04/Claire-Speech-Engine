"""Exceptions for Fish Speech."""
from cse.acoustic.backend.exceptions import BackendError

class FishSpeechInitializationError(BackendError): pass
class SpeechGenerationError(BackendError): pass
