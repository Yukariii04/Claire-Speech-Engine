"""Tests for CAM Model Downloader and Cache Manager (PRD-028 §5, §23)."""

import os
from pathlib import Path
import pytest

from cse.acoustic.cam.downloader import get_cam_cache_dir, resolve_cam_model_paths


class TestCAMDownloader:
    def test_cache_dir_created(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CSE_CAM_CACHE_DIR", str(tmp_path / "cache_cam"))
        cache_dir = get_cam_cache_dir()
        assert cache_dir.exists()
        assert cache_dir == tmp_path / "cache_cam"

    def test_resolve_cam_model_paths_absent_fails_explicitly_without_fabrication(self, tmp_path, monkeypatch):
        cache_dir = tmp_path / "test_models"
        monkeypatch.setenv("CSE_CAM_CACHE_DIR", str(cache_dir))
        
        # Must fail explicitly with FileNotFoundError
        with pytest.raises(FileNotFoundError) as exc_info:
            resolve_cam_model_paths(quantized=True)
        assert "Trained CAM model artifacts not found" in str(exc_info.value)
        assert "Silent fabrication of randomly initialized weights is strictly prohibited" in str(exc_info.value)
        
        # Proves no random ONNX artifacts were created
        created_onnx = list(cache_dir.glob("*.onnx"))
        assert len(created_onnx) == 0

    def test_resolve_cam_model_paths_resolves_when_present(self, tmp_path, monkeypatch):
        cache_dir = tmp_path / "test_models"
        cache_dir.mkdir(parents=True, exist_ok=True)
        monkeypatch.setenv("CSE_CAM_CACHE_DIR", str(cache_dir))

        # Place mock model files
        ac_mock = cache_dir / "cam_acoustic_int8.onnx"
        voc_mock = cache_dir / "cam_vocoder_int8.onnx"
        ac_mock.write_bytes(b"mock_acoustic")
        voc_mock.write_bytes(b"mock_vocoder")

        ac_path, voc_path = resolve_cam_model_paths(quantized=True)
        assert ac_path == ac_mock
        assert voc_path == voc_mock
