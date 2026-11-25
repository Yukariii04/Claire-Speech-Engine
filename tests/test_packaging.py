import subprocess
import sys
import zipfile

import cse

def test_version_exposed():
    assert hasattr(cse, "__version__")
    assert isinstance(cse.__version__, str)
    assert cse.__version__ == "1.0.5"

def test_public_imports():
    from cse import SpeechEngine
    assert SpeechEngine is not None

def test_cli_entry_point():
    # Test that the cse command works
    result = subprocess.run(["cse", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Usage" in result.stdout or "help" in result.stdout

def test_build_success(tmp_path):
    result = subprocess.run([sys.executable, "-m", "build", "--no-isolation", "--outdir", str(tmp_path)], capture_output=True, text=True)
    assert result.returncode == 0

def test_wheel_excludes_legacy_compiler(tmp_path):
    """Verify cse.performance.compiler* is excluded from the built wheel."""
    result = subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--no-isolation", "--outdir", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    wheels = list(tmp_path.glob("*.whl"))
    assert wheels, "No wheel file found after build"
    with zipfile.ZipFile(wheels[0]) as zf:
        names = zf.namelist()
    compiler_entries = [n for n in names if "performance/compiler" in n or "performance\\compiler" in n]
    assert compiler_entries == [], f"Legacy compiler leaked into wheel: {compiler_entries}"
