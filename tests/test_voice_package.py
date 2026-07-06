"""Tests for Voice Package System (PRD-007 §12)."""

from __future__ import annotations

import pytest
import yaml

from cse.voice import (
    load_voice_package,
    register_voice_package,
    get_voice_package,
    list_voice_packages,
    PackageRegistry,
    InvalidVoicePackageError,
    VoicePackageNotFoundError,
    VoicePackageError
)


@pytest.fixture
def valid_metadata_yaml():
    return {
        "id": "claire_test",
        "name": "Claire",
        "version": "1.0.0",
        "author": "CSE",
        "language": "en",
        "backend": "dummy",
        "sample_rate": 24000,
        "channels": 1,
        "description": "Test",
        "license": "MIT"
    }


def test_load_valid_package(tmp_path, valid_metadata_yaml):
    pkg_dir = tmp_path / "claire"
    pkg_dir.mkdir()
    meta_path = pkg_dir / "metadata.yaml"
    
    with open(meta_path, "w") as f:
        yaml.dump(valid_metadata_yaml, f)
        
    pkg = load_voice_package(str(pkg_dir))
    assert pkg.metadata.id == "claire_test"
    assert pkg.metadata.sample_rate == 24000
    assert str(pkg.path) == str(pkg_dir)

def test_load_missing_directory(tmp_path):
    with pytest.raises(VoicePackageNotFoundError):
        load_voice_package(str(tmp_path / "does_not_exist"))

def test_load_missing_metadata(tmp_path):
    pkg_dir = tmp_path / "claire"
    pkg_dir.mkdir()
    
    with pytest.raises(InvalidVoicePackageError, match="metadata.yaml not found"):
        load_voice_package(str(pkg_dir))

def test_load_invalid_metadata_type(tmp_path):
    pkg_dir = tmp_path / "claire"
    pkg_dir.mkdir()
    meta_path = pkg_dir / "metadata.yaml"
    
    with open(meta_path, "w") as f:
        f.write("just a string")
        
    with pytest.raises(InvalidVoicePackageError, match="must contain a dictionary"):
        load_voice_package(str(pkg_dir))

def test_validation_missing_field(tmp_path, valid_metadata_yaml):
    del valid_metadata_yaml["sample_rate"]
    
    pkg_dir = tmp_path / "claire"
    pkg_dir.mkdir()
    meta_path = pkg_dir / "metadata.yaml"
    
    with open(meta_path, "w") as f:
        yaml.dump(valid_metadata_yaml, f)
        
    with pytest.raises(InvalidVoicePackageError, match="Missing required field: sample_rate"):
        load_voice_package(str(pkg_dir))

def test_registry_operations(tmp_path, valid_metadata_yaml):
    pkg_dir = tmp_path / "claire"
    pkg_dir.mkdir()
    meta_path = pkg_dir / "metadata.yaml"
    
    with open(meta_path, "w") as f:
        yaml.dump(valid_metadata_yaml, f)
        
    pkg = load_voice_package(str(pkg_dir))
    
    registry = PackageRegistry()
    registry.register(pkg)
    
    assert "claire_test" in registry.list_packages()
    assert registry.get("claire_test") == pkg
    
    # Duplicate registration
    with pytest.raises(VoicePackageError):
        registry.register(pkg)
        
    # Removal
    registry.remove("claire_test")
    assert "claire_test" not in registry.list_packages()
    
    with pytest.raises(VoicePackageNotFoundError):
        registry.get("claire_test")
