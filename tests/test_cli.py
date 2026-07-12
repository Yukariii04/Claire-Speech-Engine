"""Tests for the Developer Experience CLI (PRD-010)."""

import subprocess
import sys
from pathlib import Path

from cse.cli.parser import create_parser
from cse.cli.commands import command_version, command_voices

CSE_PY = str(Path(__file__).resolve().parents[1] / "cse.py")


def test_parser_creation():
    parser = create_parser()
    assert parser.prog == "cse"

def test_help_command():
    result = subprocess.run([sys.executable, CSE_PY, "help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Available commands" in result.stdout or "usage" in result.stdout.lower()

def test_help_flag():
    result = subprocess.run([sys.executable, CSE_PY, "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Available commands" in result.stdout or "usage" in result.stdout.lower()

def test_version_command():
    result = subprocess.run([sys.executable, CSE_PY, "version"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Claire Speech Engine" in result.stdout

def test_voices_command():
    result = subprocess.run([sys.executable, CSE_PY, "voices"], capture_output=True, text=True)
    assert result.returncode == 0
    # PRD-015: voices now shows backend headers
    assert "KOKORO" in result.stdout

def test_speak_command_missing_args():
    result = subprocess.run([sys.executable, CSE_PY, "speak"], capture_output=True, text=True)
    assert result.returncode != 0
    assert "required" in result.stderr.lower()

def test_speak_command_invalid_voice():
    result = subprocess.run(
        [sys.executable, CSE_PY, "speak", "--voice", "invalid_123", "--text", "Test"],
        capture_output=True, text=True
    )
    # Should fail cleanly with human-readable message, not traceback
    assert result.returncode == 1
    assert "Error:" in result.stdout
    assert "Traceback" not in result.stderr
