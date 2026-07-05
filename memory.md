# Claire Speech Engine — Memory

> Context store for architecture, lore, decisions, and state.

---

## Project Identity

| Field        | Value                          |
|--------------|--------------------------------|
| **Name**     | Claire Speech Engine (CSE)     |
| **PRD**      | PRD-001 — Project Bootstrap & Foundation |
| **Goal**     | Production-grade repo scaffold — **no speech features** |
| **Python**   | ≥ 3.12                         |
| **Version**  | 0.1.0                          |

---

## PRD-001 Scope Summary

### What to build
- Repository structure (dirs + base files)
- `pyproject.toml` packaging with pinned dependency whitelist
- Entry point `cse.py` → calls `cse.runtime.bootstrap()`
- **Runtime bootstrap** (`src/cse/runtime/bootstrap.py`): config → logger → registry → runtime → banner → exit
- **Configuration system** (`src/cse/config/`): YAML-based, env overrides, defaults, validation, hot-reload stub
- **Logger**: Centralized via `loguru`, colorized, timestamped — no `print()`
- **Module Registry**: Register/discover pattern, initially empty
- **Plugin System**: Architecture only (`src/cse/plugins/`), interfaces: `initialize()`, `shutdown()`, `metadata()`
- **CLI**: `--help`, `--version`, `--debug` only
- **Tests**: Real tests for config, logger, bootstrap, CLI, registry
- **Benchmarks**: Bootstrap timing < 300 ms
- **README.md**: Install, goals, structure, running, dev, contributing

### What is forbidden
Tokenizer, Prosody, Emotion, Speech, Streaming, TTS, Phonemes, Models, Training, Inference, anything AI-related.

### Public API surface
`bootstrap()`, `shutdown()`, `get_logger()`, `get_config()`, `get_registry()`

---

## Allowed Dependencies (runtime)

| Package            | Purpose           |
|--------------------|-------------------|
| `torch`            | Future ML runtime |
| `numpy`            | Numerics          |
| `onnxruntime`      | Inference         |
| `sounddevice`      | Audio I/O         |
| `soundfile`        | Audio file I/O    |
| `pyyaml`           | Config parsing    |
| `rich`             | Console output    |
| `loguru`           | Logging           |
| `pytest`           | Testing           |
| `pytest-benchmark` | Benchmarking      |

---

## Architecture Decisions

### AD-001: cse.py name collision
`cse.py` at the project root shadows the `cse` package in `src/`. Resolved with:
- `cse.py`: ALL code inside `if __name__ == "__main__":` guard. Manipulates `sys.path` to swap CWD for `src/` and clears `sys.modules["cse"]` before importing the package.
- `conftest.py`: Force-loads the `cse` package via `importlib.util` directly from `src/cse/__init__.py` into `sys.modules`, bypassing Python's normal path-based resolution.
- `pyproject.toml`: Sets `pythonpath = ["src"]` for pytest.

### AD-002: Banner output via Rich Console
Startup banner uses `rich.Console` (clean text, no timestamps). All other log output goes through `loguru` (timestamped, colorized, leveled). This satisfies both the PRD's expected banner format and the "no print()" rule.

---

## Active State

| Key             | Value               |
|-----------------|---------------------|
| **Current PRD** | PRD-001             |
| **Phase**       | ✅ Complete          |
| **Blockers**    | None                |

---

## Verification Results

| Criterion                | Status | Detail                         |
|--------------------------|--------|--------------------------------|
| Project installs         | ✅     | `pip install -e ".[dev]"` OK   |
| Runtime starts           | ✅     | Banner matches PRD expected output |
| Runtime shuts down       | ✅     | `shutdown()` test passes       |
| Logger works             | ✅     | All 5 levels tested            |
| Configuration loads      | ✅     | Load, dotted-key, env override, reload |
| Tests pass               | ✅     | 24/24 passed                   |
| Benchmarks execute       | ✅     | Mean 2.08 ms (target < 300 ms) |
| Documentation complete   | ✅     | README with all required sections |
