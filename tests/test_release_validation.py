"""Release validation tests (PRD-012 §7).

Verifies all release assets and metadata are present and correct.
"""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_readme_exists():
    assert (ROOT / "README.md").exists()
    content = (ROOT / "README.md").read_text()
    for section in ["Installation", "Quick Start", "CLI", "Python API", "Examples", "Roadmap", "License"]:
        assert section in content, f"README missing '{section}' section"


def test_license_exists():
    assert (ROOT / "LICENSE").exists()


def test_pyproject_metadata():
    content = (ROOT / "pyproject.toml").read_text()
    for field in ["name", "version", "description", "license", "authors", "keywords", "classifiers", "requires-python"]:
        assert field in content, f"pyproject.toml missing '{field}'"


def test_examples_exist():
    examples = ROOT / "examples"
    assert examples.is_dir()
    py_files = list(examples.glob("*.py"))
    assert len(py_files) >= 1, "No example scripts found"


def test_requirements_exist():
    assert (ROOT / "requirements.txt").exists()


def test_package_builds():
    result = subprocess.run(
        [sys.executable, "-m", "build", "--no-isolation"],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    assert result.returncode == 0, f"Build failed: {result.stderr}"


def test_public_import():
    from cse import SpeechEngine
    assert SpeechEngine is not None


def test_version_string():
    import cse
    assert isinstance(cse.__version__, str)
    assert len(cse.__version__) > 0


def test_cli_entry_point():
    result = subprocess.run(["cse", "--help"], capture_output=True, text=True)
    assert result.returncode == 0
