"""Voice Package Registry (PRD-007 §9)."""

from __future__ import annotations

import threading

from cse.voice.exceptions import VoicePackageError, VoicePackageNotFoundError
from cse.voice.package import VoicePackage


class PackageRegistry:
    """Thread-safe registry for loaded Voice Packages."""

    def __init__(self) -> None:
        self._packages: dict[str, VoicePackage] = {}
        self._lock = threading.RLock()

    def register(self, package: VoicePackage) -> None:
        """Register a VoicePackage."""
        package_id = package.metadata.id
        with self._lock:
            if package_id in self._packages:
                raise VoicePackageError(f"Package '{package_id}' is already registered.")
            self._packages[package_id] = package

    def remove(self, package_id: str) -> None:
        """Remove a VoicePackage by ID."""
        with self._lock:
            if package_id not in self._packages:
                raise VoicePackageNotFoundError(f"Package '{package_id}' not found.")
            del self._packages[package_id]

    def get(self, package_id: str) -> VoicePackage:
        """Lookup a VoicePackage by ID."""
        with self._lock:
            if package_id not in self._packages:
                raise VoicePackageNotFoundError(f"Package '{package_id}' not found.")
            return self._packages[package_id]

    def list_packages(self) -> list[str]:
        """List all registered VoicePackage IDs."""
        with self._lock:
            return list(self._packages.keys())
