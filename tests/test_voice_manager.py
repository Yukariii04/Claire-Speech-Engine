"""Tests for VoiceManager."""

from __future__ import annotations

import pytest
import yaml

from cse.runtime.voice.exceptions import VoiceNotFoundError
from cse.runtime.voice.manager import VoiceManager


class TestVoiceManager:
    def test_load_voice_success(self, tmp_path):
        voice_dir = tmp_path / "claire"
        voice_dir.mkdir(parents=True)
        meta_file = voice_dir / "metadata.yaml"
        
        metadata = {
            "id": "claire",
            "name": "Claire",
            "version": "1.0.0",
            "language": "en",
            "backend": "default"
        }
        
        with open(meta_file, "w") as f:
            yaml.dump(metadata, f)
            
        manager = VoiceManager(voices_dir=str(tmp_path))
        manager.load_voice("claire")
        
        loaded = manager.get_loaded_voice()
        assert loaded is not None
        assert loaded["name"] == "Claire"

    def test_load_voice_not_found_raises(self, tmp_path):
        manager = VoiceManager(voices_dir=str(tmp_path))
        with pytest.raises(VoiceNotFoundError):
            manager.load_voice("unknown_voice")

    def test_unload_voice(self, tmp_path):
        voice_dir = tmp_path / "claire"
        voice_dir.mkdir(parents=True)
        meta_file = voice_dir / "metadata.yaml"
        with open(meta_file, "w") as f:
            yaml.dump({"id": "claire"}, f)
            
        manager = VoiceManager(voices_dir=str(tmp_path))
        manager.load_voice("claire")
        assert manager.get_loaded_voice() is not None
        
        manager.unload_voice()
        assert manager.get_loaded_voice() is None
