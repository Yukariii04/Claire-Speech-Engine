"""Runtime bootstrap — linear startup sequence for Claire Speech Engine."""

from __future__ import annotations

import argparse
import sys
from typing import NoReturn

from rich.console import Console

from cse.config.manager import ConfigManager, _set_config
from cse.core.logger import setup_logger
from cse.core.registry import ModuleRegistry, _set_registry


_console = Console()
_runtime_ready = False


def bootstrap() -> None:
    """Boot the Claire Speech Engine.

    Sequence:
        1. Parse CLI arguments
        2. Initialise configuration
        3. Initialise logger
        4. Initialise module registry
        5. Print startup banner
        6. Mark runtime ready
    """
    global _runtime_ready

    args = _parse_cli()

    # 1 — Configuration
    config = ConfigManager()
    config.load()
    _set_config(config)

    engine_name: str = config.get("engine.name", "Claire Speech Engine")
    engine_version: str = config.get("engine.version", "0.1.0")

    # 2 — Logger
    debug = args.debug or config.get("runtime.debug", False)
    setup_logger(debug=debug)

    # 3 — Module registry
    registry = ModuleRegistry()
    _set_registry(registry)

    # 4 — Banner
    _print_banner(engine_name, engine_version)

    _runtime_ready = True


def shutdown() -> None:
    """Clean shutdown of the runtime."""
    global _runtime_ready
    _runtime_ready = False


# ------------------------------------------------------------------
# Internal
# ------------------------------------------------------------------


def _parse_cli() -> argparse.Namespace:
    """Parse ``--help``, ``--version``, ``--debug``."""
    parser = argparse.ArgumentParser(
        prog="cse",
        description="Claire Speech Engine — production-grade speech synthesis.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="Claire Speech Engine 0.1.0",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug-level logging.",
    )
    return parser.parse_args()


def _print_banner(name: str, version: str) -> None:
    """Print the startup banner to the console."""
    _console.print(f"{name}")
    _console.print(f"Version {version}")
    _console.print()
    _console.print("Configuration Loaded")
    _console.print("Logger Initialized")
    _console.print("Module Registry Initialized")
    _console.print("Runtime Ready")
