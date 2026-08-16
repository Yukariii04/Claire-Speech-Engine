"""Tests for Backend Voice Discovery, Validation & Selection with KittenTTS."""

import json
import os
import pytest
from pathlib import Path
from unittest.mock import patch


# ── Backend list_voices / validate_voice ──────────────────────────────

class TestKittenTTSVoiceDiscovery:
    def test_list_voices_returns_list(self):
        from cse.backends.kittentts.backend import KittenTTSBackend
        backend = KittenTTSBackend()
        voices = backend.list_voices()
        assert isinstance(voices, list)
        assert len(voices) == 8

    def test_list_voices_has_required_keys(self):
        from cse.backends.kittentts.backend import KittenTTSBackend
        backend = KittenTTSBackend()
        for v in backend.list_voices():
            assert "id" in v
            assert "name" in v
            assert "language" in v
            assert "gender" in v

    def test_validate_voice_known(self):
        from cse.backends.kittentts.backend import KittenTTSBackend
        backend = KittenTTSBackend()
        assert backend.validate_voice("expr-voice-2-f") is True
        assert backend.validate_voice("expr-voice-2-m") is True

    def test_validate_voice_unknown(self):
        from cse.backends.kittentts.backend import KittenTTSBackend
        backend = KittenTTSBackend()
        assert backend.validate_voice("nonexistent_voice_xyz") is False

    def test_validate_voice_alias(self):
        from cse.backends.kittentts.backend import KittenTTSBackend
        backend = KittenTTSBackend()
        assert backend.validate_voice("Bella") is True
        assert backend.validate_voice("Jasper") is True
        assert backend.validate_voice("Leo") is True

    def test_default_voice_in_list(self):
        from cse.backends.kittentts.backend import KittenTTSBackend
        backend = KittenTTSBackend()
        ids = [v["id"] for v in backend.list_voices()]
        assert "expr-voice-2-f" in ids


# ── AcousticBackend interface defaults ────────────────────────────────

class TestInterfaceDefaults:
    def test_base_list_voices_empty(self):
        from cse.acoustic.backend.dummy_backend import DummyBackend
        backend = DummyBackend()
        # DummyBackend inherits from AcousticBackend; list_voices returns []
        voices = backend.list_voices()
        assert voices == []

    def test_base_validate_voice_accepts_anything_when_no_voices(self):
        from cse.acoustic.backend.dummy_backend import DummyBackend
        backend = DummyBackend()
        # No voices listed → accept anything
        assert backend.validate_voice("literally_anything") is True


# ── User Configuration ────────────────────────────────────────────────

class TestUserConfig:
    def test_load_config_missing_file(self, tmp_path):
        with patch("cse.config.user_config._config_dir", return_value=tmp_path):
            from cse.config.user_config import load_config
            assert load_config() == {}

    def test_save_and_load_config(self, tmp_path):
        with patch("cse.config.user_config._config_dir", return_value=tmp_path):
            from cse.config.user_config import save_config, load_config
            save_config({"backend": "kittentts", "voice": "expr-voice-2-f"})
            cfg = load_config()
            assert cfg["backend"] == "kittentts"
            assert cfg["voice"] == "expr-voice-2-f"

    def test_set_and_get_preference(self, tmp_path):
        with patch("cse.config.user_config._config_dir", return_value=tmp_path):
            from cse.config.user_config import set_preference, get_preference
            set_preference("backend", "kittentts")
            assert get_preference("backend") == "kittentts"

    def test_clear_preferences(self, tmp_path):
        with patch("cse.config.user_config._config_dir", return_value=tmp_path):
            from cse.config.user_config import set_preference, clear_preferences, load_config
            set_preference("backend", "kittentts")
            clear_preferences()
            assert load_config() == {}

    def test_get_preference_missing_key(self, tmp_path):
        with patch("cse.config.user_config._config_dir", return_value=tmp_path):
            from cse.config.user_config import get_preference
            assert get_preference("nonexistent") is None


# ── VoiceRuntime changes ──────────────────────────────────────────────

class TestVoiceRuntimeVoiceManagement:
    def test_load_voice_kittentts_native(self):
        """Loading a known KittenTTS voice should succeed without VoicePackage."""
        from cse.runtime.voice.runtime import VoiceRuntime
        runtime = VoiceRuntime()
        runtime.initialize()
        runtime.load_backend("kittentts")
        # This should NOT raise — backend validates the voice natively
        runtime.load_voice("expr-voice-2-f")
        runtime.shutdown()

    def test_load_voice_invalid_raises(self):
        """Loading a voice that doesn't belong to the backend should raise."""
        from cse.runtime.voice.runtime import VoiceRuntime
        from cse.runtime.voice.exceptions import VoiceNotFoundError
        runtime = VoiceRuntime()
        runtime.initialize()
        runtime.load_backend("kittentts")
        with pytest.raises(VoiceNotFoundError, match="not available"):
            runtime.load_voice("completely_bogus_voice")
        runtime.shutdown()

    def test_get_backend_id(self):
        from cse.runtime.voice.runtime import VoiceRuntime
        runtime = VoiceRuntime()
        runtime.initialize()
        assert runtime.get_backend_id() == "dummy"
        runtime.load_backend("kittentts")
        assert runtime.get_backend_id() == "kittentts"
        runtime.shutdown()

    def test_available_backend_ids(self):
        from cse.runtime.voice.runtime import VoiceRuntime
        ids = VoiceRuntime.available_backend_ids()
        assert "kittentts" in ids
        assert "dummy" not in ids


# ── SpeechEngine changes ─────────────────────────────────────────────

class TestSpeechEngineVoiceManagement:
    def test_list_voices_returns_backend_voices(self):
        from cse import SpeechEngine
        engine = SpeechEngine()
        engine.load_backend("kittentts")
        voices = engine.list_voices()
        assert isinstance(voices, list)
        assert len(voices) == 8
        assert all("id" in v for v in voices)
        engine.shutdown()

    def test_load_voice_no_args_uses_default(self):
        """load_voice() with no args should pick the backend's default."""
        from cse import SpeechEngine
        engine = SpeechEngine()
        engine.load_backend("kittentts")
        with patch("cse.config.user_config.get_preference", return_value=None):
            # Should not raise
            engine.load_voice()
        engine.shutdown()

    def test_version_bumped(self):
        from cse import SpeechEngine
        engine = SpeechEngine()
        assert engine.get_version() == "1.0.5"
        engine.shutdown()

    def test_backend_switch_resets_voice(self):
        from cse import SpeechEngine
        engine = SpeechEngine()
        engine.load_backend("kittentts")
        engine.load_voice("expr-voice-2-f")
        engine.load_backend("dummy")
        # Voice should be reset after switching backend
        with pytest.raises(Exception):
            engine.speak("test")
        engine.shutdown()


# ── CLI ───────────────────────────────────────────────────────────────

class TestCLIVoiceCommands:
    def test_parser_has_voice_command(self):
        from cse.cli.parser import create_parser
        parser = create_parser()
        args = parser.parse_args(["voice", "current"])
        assert args.command == "voice"
        assert args.voice_command == "current"

    def test_parser_voice_set(self):
        from cse.cli.parser import create_parser
        parser = create_parser()
        args = parser.parse_args(["voice", "set", "expr-voice-2-f"])
        assert args.command == "voice"
        assert args.voice_command == "set"
        assert args.voice == "expr-voice-2-f"

    def test_parser_voice_reset(self):
        from cse.cli.parser import create_parser
        parser = create_parser()
        args = parser.parse_args(["voice", "reset"])
        assert args.voice_command == "reset"

    def test_command_voice_current_no_prefs(self, tmp_path):
        """voice current with no saved config should print defaults message."""
        import argparse
        with patch("cse.config.user_config._config_dir", return_value=tmp_path):
            from cse.cli.commands import command_voice
            args = argparse.Namespace(voice_command="current")
            result = command_voice(args)
            assert result == 0

    def test_command_voice_set_valid(self, tmp_path):
        import argparse
        with patch("cse.config.user_config._config_dir", return_value=tmp_path):
            from cse.cli.commands import command_voice
            args = argparse.Namespace(voice_command="set", voice="expr-voice-2-f")
            result = command_voice(args)
            assert result == 0

            from cse.config.user_config import get_preference
            assert get_preference("voice") == "expr-voice-2-f"

    def test_command_voice_set_invalid_voice(self, tmp_path):
        import argparse
        with patch("cse.config.user_config._config_dir", return_value=tmp_path):
            from cse.cli.commands import command_voice
            args = argparse.Namespace(voice_command="set", voice="bogus_voice")
            result = command_voice(args)
            assert result == 1

    def test_command_voice_reset(self, tmp_path):
        import argparse
        with patch("cse.config.user_config._config_dir", return_value=tmp_path):
            from cse.config.user_config import set_preference
            set_preference("voice", "expr-voice-3-m")
            from cse.cli.commands import command_voice
            args = argparse.Namespace(voice_command="reset")
            result = command_voice(args)
            assert result == 0
