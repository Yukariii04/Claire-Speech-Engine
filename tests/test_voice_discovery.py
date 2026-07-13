"""Tests for PRD-015: Backend Voice Discovery, Validation & Selection."""

import json
import os
import pytest
from pathlib import Path
from unittest.mock import patch


# ── Backend list_voices / validate_voice ──────────────────────────────

class TestKokoroVoiceDiscovery:
    def test_list_voices_returns_list(self):
        from cse.backends.kokoro.backend import KokoroBackend
        backend = KokoroBackend()
        voices = backend.list_voices()
        assert isinstance(voices, list)
        assert len(voices) > 0

    def test_list_voices_has_required_keys(self):
        from cse.backends.kokoro.backend import KokoroBackend
        backend = KokoroBackend()
        for v in backend.list_voices():
            assert "id" in v
            assert "name" in v

    def test_validate_voice_known(self):
        from cse.backends.kokoro.backend import KokoroBackend
        backend = KokoroBackend()
        assert backend.validate_voice("af_heart") is True

    def test_validate_voice_unknown(self):
        from cse.backends.kokoro.backend import KokoroBackend
        backend = KokoroBackend()
        assert backend.validate_voice("nonexistent_voice_xyz") is False

    def test_default_voice_in_list(self):
        from cse.backends.kokoro.backend import KokoroBackend
        backend = KokoroBackend()
        ids = [v["id"] for v in backend.list_voices()]
        assert "af_heart" in ids





class TestStyleTTS2VoiceDiscovery:
    def test_list_voices_returns_list(self):
        from cse.backends.styletts2.backend import StyleTTS2Backend
        backend = StyleTTS2Backend()
        voices = backend.list_voices()
        assert isinstance(voices, list)
        assert len(voices) > 0

    def test_validate_voice_default(self):
        from cse.backends.styletts2.backend import StyleTTS2Backend
        backend = StyleTTS2Backend()
        assert backend.validate_voice("claire_neutral") is True


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
            save_config({"backend": "kokoro", "voice": "af_bella"})
            cfg = load_config()
            assert cfg["backend"] == "kokoro"
            assert cfg["voice"] == "af_bella"

    def test_set_and_get_preference(self, tmp_path):
        with patch("cse.config.user_config._config_dir", return_value=tmp_path):
            from cse.config.user_config import set_preference, get_preference
            set_preference("backend", "fishspeech")
            assert get_preference("backend") == "fishspeech"

    def test_clear_preferences(self, tmp_path):
        with patch("cse.config.user_config._config_dir", return_value=tmp_path):
            from cse.config.user_config import set_preference, clear_preferences, load_config
            set_preference("backend", "kokoro")
            clear_preferences()
            assert load_config() == {}

    def test_get_preference_missing_key(self, tmp_path):
        with patch("cse.config.user_config._config_dir", return_value=tmp_path):
            from cse.config.user_config import get_preference
            assert get_preference("nonexistent") is None


# ── VoiceRuntime PRD-015 changes ──────────────────────────────────────

class TestVoiceRuntimePRD015:
    def test_load_voice_kokoro_native(self):
        """Loading a known Kokoro voice should succeed without VoicePackage."""
        from cse.runtime.voice.runtime import VoiceRuntime
        runtime = VoiceRuntime()
        runtime.initialize()
        runtime.load_backend("kokoro")
        # This should NOT raise — backend validates the voice natively
        runtime.load_voice("af_heart")
        runtime.shutdown()

    def test_load_voice_invalid_raises(self):
        """Loading a voice that doesn't belong to the backend should raise."""
        from cse.runtime.voice.runtime import VoiceRuntime
        from cse.runtime.voice.exceptions import VoiceNotFoundError
        runtime = VoiceRuntime()
        runtime.initialize()
        runtime.load_backend("kokoro")
        with pytest.raises(VoiceNotFoundError, match="not available"):
            runtime.load_voice("completely_bogus_voice")
        runtime.shutdown()

    def test_get_backend_id(self):
        from cse.runtime.voice.runtime import VoiceRuntime
        runtime = VoiceRuntime()
        runtime.initialize()
        assert runtime.get_backend_id() == "dummy"
        runtime.load_backend("kokoro")
        assert runtime.get_backend_id() == "kokoro"
        runtime.shutdown()

    def test_available_backend_ids(self):
        from cse.runtime.voice.runtime import VoiceRuntime
        ids = VoiceRuntime.available_backend_ids()
        assert "kokoro" in ids
        assert "styletts2" in ids
        assert "dummy" not in ids


# ── SpeechEngine PRD-015 changes ─────────────────────────────────────

class TestSpeechEnginePRD015:
    def test_list_voices_returns_backend_voices(self):
        from cse import SpeechEngine
        engine = SpeechEngine()
        engine.load_backend("kokoro")
        voices = engine.list_voices()
        assert isinstance(voices, list)
        assert len(voices) > 0
        assert all("id" in v for v in voices)
        engine.shutdown()

    def test_load_voice_no_args_uses_default(self):
        """load_voice() with no args should pick the backend's default."""
        from cse import SpeechEngine
        engine = SpeechEngine()
        engine.load_backend("kokoro")
        with patch("cse.config.user_config.get_preference", return_value=None):
            # Should not raise
            engine.load_voice()
        engine.shutdown()

    def test_version_bumped(self):
        from cse import SpeechEngine
        engine = SpeechEngine()
        assert engine.get_version() == "1.0.4"
        engine.shutdown()

    def test_backend_switch_resets_voice(self):
        from cse import SpeechEngine
        engine = SpeechEngine()
        engine.load_backend("kokoro")
        engine.load_voice("af_heart")
        # ponytail: use dummy backend to avoid needing styletts2 installed
        engine.load_backend("dummy")
        # Voice should be reset after switching backend
        with pytest.raises(Exception):
            engine.speak("test")
        engine.shutdown()


# ── CLI ───────────────────────────────────────────────────────────────

class TestCLIPRD015:
    def test_parser_has_voice_command(self):
        from cse.cli.parser import create_parser
        parser = create_parser()
        args = parser.parse_args(["voice", "current"])
        assert args.command == "voice"
        assert args.voice_command == "current"

    def test_parser_voice_set(self):
        from cse.cli.parser import create_parser
        parser = create_parser()
        args = parser.parse_args(["voice", "set", "kokoro", "af_bella"])
        assert args.command == "voice"
        assert args.voice_command == "set"
        assert args.backend == "kokoro"
        assert args.voice == "af_bella"

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
            args = argparse.Namespace(voice_command="set", backend="kokoro", voice="af_heart")
            result = command_voice(args)
            assert result == 0

            from cse.config.user_config import get_preference
            assert get_preference("backend") == "kokoro"
            assert get_preference("voice") == "af_heart"

    def test_command_voice_set_invalid_voice(self, tmp_path):
        import argparse
        with patch("cse.config.user_config._config_dir", return_value=tmp_path):
            from cse.cli.commands import command_voice
            args = argparse.Namespace(voice_command="set", backend="kokoro", voice="bogus_voice")
            result = command_voice(args)
            assert result == 1

    def test_command_voice_set_invalid_backend(self, tmp_path):
        import argparse
        with patch("cse.config.user_config._config_dir", return_value=tmp_path):
            from cse.cli.commands import command_voice
            args = argparse.Namespace(voice_command="set", backend="not_a_backend", voice="x")
            result = command_voice(args)
            assert result == 1

    def test_command_voice_reset(self, tmp_path):
        import argparse
        with patch("cse.config.user_config._config_dir", return_value=tmp_path):
            from cse.config.user_config import set_preference
            set_preference("backend", "kokoro")
            from cse.cli.commands import command_voice
            args = argparse.Namespace(voice_command="reset")
            result = command_voice(args)
            assert result == 0
