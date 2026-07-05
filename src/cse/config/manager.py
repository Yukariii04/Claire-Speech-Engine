"""Configuration manager — YAML-based with env overrides and validation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


_DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[3] / "configs" / "default.yaml"

# ponytail: single global instance, factory if multi-config ever needed
_instance: ConfigManager | None = None


class ConfigError(Exception):
    """Raised on configuration load or validation failure."""


class ConfigManager:
    """Loads, validates, and serves YAML configuration with env overrides.

    Attributes:
        data: The merged configuration dictionary.
    """

    def __init__(self, config_path: Path | str | None = None) -> None:
        self._path = Path(config_path) if config_path else _DEFAULT_CONFIG_PATH
        self.data: dict[str, Any] = {}
        self._loaded = False

    # ------------------------------------------------------------------
    # Public
    # ------------------------------------------------------------------

    def load(self) -> None:
        """Load YAML file, apply env overrides, validate."""
        raw = self._read_yaml()
        self.data = self._apply_env_overrides(raw)
        self._validate()
        self._loaded = True

    def get(self, dotted_key: str, default: Any = None) -> Any:
        """Retrieve a value by dotted path (e.g. ``engine.version``).

        Args:
            dotted_key: Dot-separated path into the config tree.
            default: Fallback if the key is missing.

        Returns:
            The config value or *default*.
        """
        node: Any = self.data
        for part in dotted_key.split("."):
            if isinstance(node, dict) and part in node:
                node = node[part]
            else:
                return default
        return node

    @property
    def is_loaded(self) -> bool:
        """Whether configuration has been loaded successfully."""
        return self._loaded

    def reload(self) -> None:
        """Hot-reload configuration from disk.

        Re-reads the YAML file and re-applies env overrides.
        """
        self.load()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _read_yaml(self) -> dict[str, Any]:
        if not self._path.exists():
            raise ConfigError(f"Config file not found: {self._path}")
        with self._path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if not isinstance(data, dict):
            raise ConfigError(f"Config root must be a mapping, got {type(data).__name__}")
        return data

    @staticmethod
    def _apply_env_overrides(data: dict[str, Any]) -> dict[str, Any]:
        """Override config values with ``CSE_<SECTION>_<KEY>`` env vars.

        Example: ``CSE_RUNTIME_DEBUG=1`` overrides ``runtime.debug``.
        """
        prefix = "CSE_"
        for key, value in os.environ.items():
            if not key.startswith(prefix):
                continue
            parts = key[len(prefix) :].lower().split("_")
            node = data
            for part in parts[:-1]:
                node = node.setdefault(part, {})
            # ponytail: coerce booleans and ints, good enough for config
            node[parts[-1]] = _coerce(value)
        return data

    def _validate(self) -> None:
        """Ensure required top-level keys exist."""
        for required in ("engine", "runtime"):
            if required not in self.data:
                raise ConfigError(f"Missing required config section: '{required}'")
        engine = self.data["engine"]
        if "name" not in engine or "version" not in engine:
            raise ConfigError("engine section must contain 'name' and 'version'")


def _coerce(value: str) -> str | bool | int | float:
    """Best-effort coerce env-var strings to Python types."""
    low = value.lower()
    if low in ("true", "1", "yes"):
        return True
    if low in ("false", "0", "no"):
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value


def get_config() -> ConfigManager:
    """Return the global ``ConfigManager`` singleton.

    Raises:
        RuntimeError: If called before the runtime has initialised config.
    """
    if _instance is None:
        raise RuntimeError("Configuration not initialised — call bootstrap() first.")
    return _instance


def _set_config(instance: ConfigManager) -> None:
    """Set the global config instance (called by bootstrap)."""
    global _instance
    _instance = instance
