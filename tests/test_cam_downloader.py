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

    def test_resolve_cam_model_paths_creates_and_resolves(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CSE_CAM_CACHE_DIR", str(tmp_path / "test_models"))
        ac_path, voc_path = resolve_cam_model_paths(quantized=True)
        assert ac_path.exists()
        assert voc_path.exists()
        assert "int8" in ac_path.name
        assert "int8" in voc_path.name
