"""Regression tests for CAM package import boundaries (PRD-028, PRD-029).

Ensures importing lightweight CAM modules does not eagerly load heavy runtimes
(onnxruntime, torch) until specifically demanded.
"""

import subprocess
import sys

import pytest


def test_cam_lightweight_import_boundary():
    """Importing cse.acoustic.cam must NOT eagerly import onnxruntime or torch."""
    code = (
        "import sys\n"
        "import cse.acoustic.cam\n"
        "assert 'onnxruntime' not in sys.modules, f'onnxruntime in sys.modules: {sys.modules.get(\"onnxruntime\")}'\n"
        "assert 'torch' not in sys.modules, f'torch in sys.modules: {sys.modules.get(\"torch\")}'\n"
        "print('PASS')\n"
    )
    res = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert res.returncode == 0, f"STDOUT: {res.stdout}\nSTDERR: {res.stderr}"
    assert "PASS" in res.stdout


def test_cam_submodules_lightweight_import():
    """Importing CAMConfig, CAMPhonemizer, Adapter, Downloader must NOT import onnxruntime or torch."""
    code = (
        "import sys\n"
        "from cse.acoustic.cam import (\n"
        "    CAMConfig,\n"
        "    CAMPhonemizer,\n"
        "    GraphToConditioningAdapter,\n"
        "    CAMConditioningTensors,\n"
        "    resolve_cam_model_paths,\n"
        ")\n"
        "assert 'onnxruntime' not in sys.modules, 'onnxruntime eagerly loaded!'\n"
        "assert 'torch' not in sys.modules, 'torch eagerly loaded!'\n"
        "print('PASS')\n"
    )
    res = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert res.returncode == 0, f"STDOUT: {res.stdout}\nSTDERR: {res.stderr}"
    assert "PASS" in res.stdout


def test_cam_backend_lazy_resolution():
    """CAMBackend should load onnxruntime on-demand when accessed."""
    code = (
        "import sys\n"
        "import cse.acoustic.cam\n"
        "assert 'onnxruntime' not in sys.modules\n"
        "# Now import CAMBackend from package\n"
        "from cse.acoustic.cam import CAMBackend\n"
        "assert CAMBackend is not None\n"
        "assert 'onnxruntime' in sys.modules\n"
        "print('PASS')\n"
    )
    res = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert res.returncode == 0, f"STDOUT: {res.stdout}\nSTDERR: {res.stderr}"
    assert "PASS" in res.stdout


def test_cam_package_all_and_dir():
    """__all__ and dir() should expose public symbols including lazy exports."""
    import cse.acoustic.cam as cam

    assert "CAMBackend" in cam.__all__
    assert "CAMBackend" in dir(cam)
    assert "CAMConfig" in cam.__all__
    assert "CAMPhonemizer" in cam.__all__
