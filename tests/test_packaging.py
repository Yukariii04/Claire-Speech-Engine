import subprocess
import sys
import tarfile
import zipfile

import cse

ALLOWED_RUNTIME_SUBPACKAGES = {
    "acoustic",
    "api",
    "backends",
    "cli",
    "config",
    "core",
    "language",
    "performance",
    "plugins",
    "runtime",
    "streaming",
    "voice",
    "_scaffold",
    "__init__.py",
    "__pycache__",
}


def _assert_runtime_package_layout(entries: list[str], *, pkg_prefix: tuple[str, ...]) -> None:
    """Assert built distribution entries contain only allowed runtime subpackages and no legacy compiler."""
    compiler_entries = [n for n in entries if "performance/compiler" in n or "performance\\compiler" in n]
    assert compiler_entries == [], f"Legacy compiler leaked into distribution: {compiler_entries}"
    prefix_len = len(pkg_prefix)
    for n in entries:
        parts = [p for p in n.replace("\\", "/").split("/") if p]
        if len(parts) > prefix_len and tuple(parts[:prefix_len]) == pkg_prefix:
            assert parts[prefix_len] in ALLOWED_RUNTIME_SUBPACKAGES, f"Unexpected package entry in distribution: {n}"


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
    """Verify only supported runtime modules are packaged and legacy compiler modules are excluded."""
    result = subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--no-isolation", "--outdir", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    wheels = list(tmp_path.glob("*.whl"))
    assert wheels, "No wheel file found after build"
    with zipfile.ZipFile(wheels[0]) as zf:
        names = zf.namelist()
    assert any(n == "cse/__init__.py" for n in names), "Runtime package root missing from wheel"
    _assert_runtime_package_layout(names, pkg_prefix=("cse",))


def test_sdist_excludes_tests_and_unlisted_packages(tmp_path):
    """Verify sdist omits the unbundled test directory and exposes only allowed runtime modules."""
    result = subprocess.run(
        [sys.executable, "-m", "build", "--sdist", "--no-isolation", "--outdir", str(tmp_path)],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    sdists = list(tmp_path.glob("*.tar.gz"))
    assert sdists, "No sdist archive found after build"
    with tarfile.open(sdists[0], "r:gz") as tf:
        names = tf.getnames()
    root_name = names[0].split("/", 1)[0]
    assert f"{root_name}/src/cse/__init__.py" in names, "Runtime package root missing from sdist"
    test_entries = [n for n in names if n == f"{root_name}/tests" or n.startswith(f"{root_name}/tests/")]
    assert test_entries == [], f"Unexpected tests directory in sdist: {test_entries}"
    _assert_runtime_package_layout(names, pkg_prefix=(root_name, "src", "cse"))
