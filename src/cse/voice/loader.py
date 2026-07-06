"""Voice Package Loader (PRD-007 §7)."""

from __future__ import annotations

from pathlib import Path
import yaml

from cse.voice.exceptions import InvalidVoicePackageError, VoicePackageNotFoundError
from cse.voice.metadata import VoiceMetadata
from cse.voice.package import VoicePackage
from cse.voice.validator import validate_metadata_dict


class PackageLoader:
    """Stateless loader for Voice Packages."""

    @staticmethod
    def load(path: Path | str) -> VoicePackage:
        """Load and validate a Voice Package from a directory."""
        package_dir = Path(path)
        
        if not package_dir.exists() or not package_dir.is_dir():
            raise VoicePackageNotFoundError(f"Package directory not found: {package_dir}")

        metadata_path = package_dir / "metadata.yaml"
        if not metadata_path.exists():
            raise InvalidVoicePackageError(f"metadata.yaml not found in {package_dir}")

        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except Exception as e:
            raise InvalidVoicePackageError(f"Failed to parse metadata.yaml: {e}") from e

        if not isinstance(data, dict):
            raise InvalidVoicePackageError("metadata.yaml must contain a dictionary")

        validate_metadata_dict(data)

        metadata = VoiceMetadata(
            id=data["id"],
            name=data["name"],
            version=data["version"],
            author=data["author"],
            language=data["language"],
            backend=data["backend"],
            sample_rate=data["sample_rate"],
            channels=data["channels"],
            description=data["description"],
            license=data["license"]
        )

        return VoicePackage(metadata=metadata, path=package_dir)
