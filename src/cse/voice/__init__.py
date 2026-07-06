"""Voice Package System."""

from __future__ import annotations

from cse.voice.exceptions import (
    InvalidVoicePackageError,
    VoicePackageError,
    VoicePackageNotFoundError,
)
from cse.voice.loader import PackageLoader
from cse.voice.metadata import VoiceMetadata
from cse.voice.package import VoicePackage
from cse.voice.registry import PackageRegistry

# Global/Default Registry instance for ease of use (as typical with package managers)
_registry = PackageRegistry()

def load_voice_package(path: str) -> VoicePackage:
    """Load a voice package from disk."""
    return PackageLoader.load(path)

def validate_voice_package(path: str) -> None:
    """Validate a voice package on disk without registering."""
    PackageLoader.load(path)

def register_voice_package(package: VoicePackage) -> None:
    """Register a loaded voice package globally."""
    _registry.register(package)

def list_voice_packages() -> list[str]:
    """List globally registered voice package IDs."""
    return _registry.list_packages()

def get_voice_package(package_id: str) -> VoicePackage:
    """Get a globally registered voice package by ID."""
    return _registry.get(package_id)

__all__ = [
    "InvalidVoicePackageError",
    "PackageLoader",
    "PackageRegistry",
    "VoiceMetadata",
    "VoicePackage",
    "VoicePackageError",
    "VoicePackageNotFoundError",
    "get_voice_package",
    "list_voice_packages",
    "load_voice_package",
    "register_voice_package",
    "validate_voice_package",
]
