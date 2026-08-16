"""Tests for the Developer Experience CLI (PRD-010, PRD-015, CLEANUP-2, CLEANUP-3)."""

import subprocess
import sys
from unittest.mock import patch
import argparse
import pytest

from cse.cli.parser import create_parser
from cse.cli.commands import command_version, command_models, command_model, command_voice


def test_parser_creation():
    parser = create_parser()
    assert parser.prog == "cse"


def test_help_command():
    result = subprocess.run([sys.executable, "-m", "cse.cli.main", "help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "models" in result.stdout
    assert "model" in result.stdout
    assert "voice" in result.stdout
    # Obsolete commands should not be in the output
    assert "voices" not in result.stdout.split()
    assert "backends" not in result.stdout.split()


def test_help_flag():
    result = subprocess.run([sys.executable, "-m", "cse.cli.main", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "models" in result.stdout
    assert "model" in result.stdout
    assert "voice" in result.stdout
    assert "voices" not in result.stdout.split()
    assert "backends" not in result.stdout.split()


def test_version_command():
    result = subprocess.run([sys.executable, "-m", "cse.cli.main", "version"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Claire Speech Engine 1.0.5" in result.stdout


def test_voices_command_is_rejected():
    """Verify that 'cse voices' is no longer a valid top-level command."""
    result = subprocess.run([sys.executable, "-m", "cse.cli.main", "voices"], capture_output=True, text=True)
    assert result.returncode != 0
    assert "invalid choice: 'voices'" in result.stderr or "invalid choice: 'voices'" in result.stdout


def test_backends_command_is_rejected():
    """Verify that 'cse backends' is no longer a valid top-level command."""
    result = subprocess.run([sys.executable, "-m", "cse.cli.main", "backends"], capture_output=True, text=True)
    assert result.returncode != 0
    assert "invalid choice: 'backends'" in result.stderr or "invalid choice: 'backends'" in result.stdout


def test_models_command():
    result = subprocess.run([sys.executable, "-m", "cse.cli.main", "models"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "kitten-tts-nano-0.8" in result.stdout
    assert "kitten-tts-micro-0.8" in result.stdout
    assert "kitten-tts-mini-0.8" in result.stdout
    assert "kitten-tts-nano-0.1" not in result.stdout


class TestCLIModelCommands:
    def test_parser_has_models_and_model_commands(self):
        parser = create_parser()
        args = parser.parse_args(["models"])
        assert args.command == "models"

        args = parser.parse_args(["model", "current"])
        assert args.command == "model"
        assert args.model_command == "current"

    def test_parser_model_set(self):
        parser = create_parser()
        args = parser.parse_args(["model", "set", "kitten-tts-micro-0.8"])
        assert args.command == "model"
        assert args.model_command == "set"
        assert args.model_id == "kitten-tts-micro-0.8"

    def test_parser_model_reset(self):
        parser = create_parser()
        args = parser.parse_args(["model", "reset"])
        assert args.model_command == "reset"

    def test_command_model_current_no_prefs(self, tmp_path):
        with patch("cse.config.user_config._config_dir", return_value=tmp_path):
            args = argparse.Namespace(model_command="current")
            result = command_model(args)
            assert result == 0

    def test_command_model_set_valid(self, tmp_path):
        with patch("cse.config.user_config._config_dir", return_value=tmp_path):
            args = argparse.Namespace(model_command="set", model_id="kitten-tts-micro-0.8")
            result = command_model(args)
            assert result == 0

            from cse.config.user_config import get_preference
            assert get_preference("model") == "kitten-tts-micro-0.8"

    def test_command_model_set_invalid(self, tmp_path):
        with patch("cse.config.user_config._config_dir", return_value=tmp_path):
            args = argparse.Namespace(model_command="set", model_id="invalid-bogus-model")
            result = command_model(args)
            assert result == 1

    def test_command_model_reset(self, tmp_path):
        with patch("cse.config.user_config._config_dir", return_value=tmp_path):
            from cse.config.user_config import set_preference, get_preference
            set_preference("model", "kitten-tts-mini-0.8")
            args = argparse.Namespace(model_command="reset")
            result = command_model(args)
            assert result == 0
            assert get_preference("model") == "kitten-tts-nano-0.8"


class TestCLIVoiceDirectSelection:
    def test_command_voice_set_alias(self, tmp_path):
        with patch("cse.config.user_config._config_dir", return_value=tmp_path):
            args = argparse.Namespace(voice_command="set", voice="Bella")
            result = command_voice(args)
            assert result == 0

            from cse.config.user_config import get_preference
            assert get_preference("voice") == "Bella"

    def test_command_voice_set_voice_id(self, tmp_path):
        with patch("cse.config.user_config._config_dir", return_value=tmp_path):
            args = argparse.Namespace(voice_command="set", voice="expr-voice-3-m")
            result = command_voice(args)
            assert result == 0

            from cse.config.user_config import get_preference
            assert get_preference("voice") == "expr-voice-3-m"

    def test_command_voice_set_invalid(self, tmp_path):
        with patch("cse.config.user_config._config_dir", return_value=tmp_path):
            args = argparse.Namespace(voice_command="set", voice="nonexistent_voice")
            result = command_voice(args)
            assert result == 1

    def test_command_voice_current(self, tmp_path):
        with patch("cse.config.user_config._config_dir", return_value=tmp_path):
            args = argparse.Namespace(voice_command="current")
            result = command_voice(args)
            assert result == 0

    def test_command_voice_reset(self, tmp_path):
        with patch("cse.config.user_config._config_dir", return_value=tmp_path):
            from cse.config.user_config import set_preference, get_preference
            set_preference("voice", "expr-voice-5-m")
            args = argparse.Namespace(voice_command="reset")
            result = command_voice(args)
            assert result == 0
            assert get_preference("voice") == "expr-voice-2-f"


class TestCLISetupCommand:
    def test_parser_setup_has_no_backend_arg(self):
        parser = create_parser()
        args = parser.parse_args(["setup"])
        assert args.command == "setup"
        # Passing an unexpected positional backend argument should fail parsing
        with pytest.raises(SystemExit):
            parser.parse_args(["setup", "kittentts"])

    def test_setup_help_does_not_expose_backend(self):
        result = subprocess.run([sys.executable, "-m", "cse.cli.main", "setup", "--help"], capture_output=True, text=True)
        assert result.returncode == 0
        assert "backend_name" not in result.stdout
        assert "Optional target backend" not in result.stdout

    def test_command_setup_success(self):
        from cse.cli.commands import command_setup
        from unittest.mock import MagicMock

        mock_proc = MagicMock()
        mock_proc.returncode = 0

        with patch("subprocess.run", return_value=mock_proc), \
             patch("cse.backends.kittentts.backend.download_all_models", return_value=[]):
            result = command_setup(argparse.Namespace())
            assert result == 0

    def test_command_setup_pip_failure(self):
        from cse.cli.commands import command_setup
        from unittest.mock import MagicMock

        mock_proc = MagicMock()
        mock_proc.returncode = 1

        with patch("subprocess.run", return_value=mock_proc) as mock_sub, \
             patch("cse.backends.kittentts.backend.download_all_models") as mock_dl:
            result = command_setup(argparse.Namespace())
            assert result == 1
            mock_sub.assert_called_once()
            # Model download must not be attempted if pip install fails
            mock_dl.assert_not_called()

    def test_command_setup_model_download_single_failure(self):
        from cse.cli.commands import command_setup
        from unittest.mock import MagicMock

        mock_proc = MagicMock()
        mock_proc.returncode = 0

        with patch("subprocess.run", return_value=mock_proc), \
             patch("cse.backends.kittentts.backend.download_all_models", return_value=["kitten-tts-micro-0.8"]):
            result = command_setup(argparse.Namespace())
            assert result == 1

    def test_command_setup_model_download_multiple_failure(self):
        from cse.cli.commands import command_setup
        from unittest.mock import MagicMock

        mock_proc = MagicMock()
        mock_proc.returncode = 0

        with patch("subprocess.run", return_value=mock_proc), \
             patch("cse.backends.kittentts.backend.download_all_models", return_value=["kitten-tts-nano-0.8", "kitten-tts-mini-0.8"]):
            result = command_setup(argparse.Namespace())
            assert result == 1

    def test_command_setup_model_download_exception(self):
        from cse.cli.commands import command_setup
        from unittest.mock import MagicMock

        mock_proc = MagicMock()
        mock_proc.returncode = 0

        with patch("subprocess.run", return_value=mock_proc), \
             patch("cse.backends.kittentts.backend.download_all_models", side_effect=RuntimeError("Hub error")):
            result = command_setup(argparse.Namespace())
            assert result == 1

