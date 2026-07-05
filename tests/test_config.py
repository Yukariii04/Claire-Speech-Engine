"""Tests for the configuration system."""

from __future__ import annotations

import os
import textwrap
from pathlib import Path

import pytest

from cse.config.manager import ConfigError, ConfigManager


@pytest.fixture()
def tmp_config(tmp_path: Path) -> Path:
    """Write a minimal valid config and return its path."""
    cfg = tmp_path / "test.yaml"
    cfg.write_text(
        textwrap.dedent("""\
            engine:
              name: Test Engine
              version: 0.0.1
            runtime:
              debug: false
        """),
        encoding="utf-8",
    )
    return cfg


@pytest.fixture()
def bad_config(tmp_path: Path) -> Path:
    """Write a config missing required fields."""
    cfg = tmp_path / "bad.yaml"
    cfg.write_text("runtime:\n  debug: true\n", encoding="utf-8")
    return cfg


class TestConfigManager:
    """ConfigManager unit tests."""

    def test_load_valid(self, tmp_config: Path) -> None:
        mgr = ConfigManager(tmp_config)
        mgr.load()
        assert mgr.is_loaded
        assert mgr.get("engine.name") == "Test Engine"
        assert mgr.get("engine.version") == "0.0.1"

    def test_dotted_key_default(self, tmp_config: Path) -> None:
        mgr = ConfigManager(tmp_config)
        mgr.load()
        assert mgr.get("nonexistent.key", "fallback") == "fallback"

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        mgr = ConfigManager(tmp_path / "nope.yaml")
        with pytest.raises(ConfigError, match="not found"):
            mgr.load()

    def test_missing_engine_section_raises(self, bad_config: Path) -> None:
        mgr = ConfigManager(bad_config)
        with pytest.raises(ConfigError, match="engine"):
            mgr.load()

    def test_env_override(self, tmp_config: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("CSE_RUNTIME_DEBUG", "true")
        mgr = ConfigManager(tmp_config)
        mgr.load()
        assert mgr.get("runtime.debug") is True

    def test_reload(self, tmp_config: Path) -> None:
        mgr = ConfigManager(tmp_config)
        mgr.load()
        assert mgr.get("engine.name") == "Test Engine"
        # Overwrite file and reload
        tmp_config.write_text(
            textwrap.dedent("""\
                engine:
                  name: Reloaded
                  version: 0.0.2
                runtime:
                  debug: true
            """),
            encoding="utf-8",
        )
        mgr.reload()
        assert mgr.get("engine.name") == "Reloaded"
