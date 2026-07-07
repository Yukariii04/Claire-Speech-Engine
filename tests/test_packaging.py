import subprocess
import sys

import cse

def test_version_exposed():
    assert hasattr(cse, "__version__")
    assert isinstance(cse.__version__, str)
    assert cse.__version__ == "0.11.0-alpha"

def test_public_imports():
    from cse import SpeechEngine
    assert SpeechEngine is not None

def test_cli_entry_point():
    # Test that the cse command works
    result = subprocess.run(["cse", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Usage" in result.stdout or "help" in result.stdout

def test_build_success():
    result = subprocess.run([sys.executable, "-m", "build"], capture_output=True, text=True)
    assert result.returncode == 0
