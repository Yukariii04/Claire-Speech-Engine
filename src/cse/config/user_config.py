"""User Configuration persistence (PRD-015 §9).

Stores user voice/backend preferences outside the package.
"""

from __future__ import annotations

import json
import os
import platform
from pathlib import Path


def _config_dir() -> Path:
    """Platform-specific config directory."""
    # ponytail: stdlib only, no appdirs dependency
    system = platform.system()
    if system == "Windows":
        base = os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")
        return Path(base) / "ClaireSpeechEngine"
    elif system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "ClaireSpeechEngine"
    else:
        xdg = os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config")
        return Path(xdg) / "claire-speech-engine"


_CONFIG_FILE = "config.json"


def _config_path() -> Path:
    return _config_dir() / _CONFIG_FILE


def load_config() -> dict:
    """Load user config. Returns empty dict if missing."""
    path = _config_path()
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def save_config(data: dict) -> None:
    """Save user config."""
    path = _config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def get_preference(key: str) -> str | None:
    """Get a single preference value."""
    return load_config().get(key)


def set_preference(key: str, value: str) -> None:
    """Set a single preference value."""
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)


def clear_preferences() -> None:
    """Remove the config file entirely."""
    path = _config_path()
    if path.exists():
        path.unlink()
