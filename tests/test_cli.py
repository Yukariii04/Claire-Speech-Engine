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
    result = subprocess.run([sys.executable, "-m", "cse.cli.main", "help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Available commands" in result.stdout or "usage" in result.stdout.lower()

def test_help_flag():
    result = subprocess.run([sys.executable, "-m", "cse.cli.main", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Available commands" in result.stdout or "usage" in result.stdout.lower()

def test_version_command():
    result = subprocess.run([sys.executable, "-m", "cse.cli.main", "version"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Claire Speech Engine" in result.stdout

def test_voices_command():
    result = subprocess.run([sys.executable, "-m", "cse.cli.main", "voices"], capture_output=True, text=True)
    assert result.returncode == 0
    # PRD-015: voices now shows backend headers
    assert "KOKORO" in result.stdout

