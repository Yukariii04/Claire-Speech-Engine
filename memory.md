# Claire Speech Engine — Memory

> Context store for architecture, lore, decisions, and state.

---

## Project Identity

| Field        | Value                          |
|--------------|--------------------------------|
| **Name**     | Claire Speech Engine (CSE)     |
| **PRD**      | PRD-001 — Project Bootstrap & Foundation |
| **Goal**     | Production-grade repo scaffold — **no speech features** |
| **Python**   | >= 3.12                         |
| **Version**  | 1.0.4                          |

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

### AD-003: Removal of Fish Speech Backend
During the transition to 1.0.4, Fish Speech was entirely removed from the production framework. Reason: Fish Speech v1.5 enforces heavy, strictly pinned dependencies (`torch<=2.4.1`, `torchaudio`, `pytorch-lightning`, etc.) which caused profound environment instability (e.g., `[WinError 127]` due to mismatched C++ extensions). This severely conflicted with lighter, more flexible backends like Kokoro and StyleTTS2. To preserve the "it just works" philosophy of CSE on Python 3.12, Fish Speech was excised.

---



## Skills Evaluation (PRD-015)

- **`ponytail`**: Used to strictly rely on native python `json`/`os`/`platform` for `user_config.py` without introducing bulky dependency libraries like `appdirs`. Also used to enforce a minimalist interactive CLI loop in `claire_cli.py` instead of pulling in `click` or `prompt_toolkit`.
- **UI/UX Skills**: Not applicable.
- **GSD Skills**: Not applicable.

---

## Active State

| Key             | Value               |
|-----------------|---------------------|
| **Current PRD** | PRD-019 (Translator Interface) |
| **Phase**       | Complete |
| **Blockers**    | None                |

---

## Verification Results (PRD-004)

| Criterion                 | Status | Detail                         |
|---------------------------|--------|--------------------------------|
| Runtime initializes       | ✅     | Transitions UNINITIALIZED->READY |
| Voice metadata loads      | ✅     | `VoiceManager` parses YAML     |
| State transitions work    | ✅     | Strictly enforced via `RuntimeState` |
| Backend registration works| ✅     | Dependency injection supported |
| Dummy backend called      | ✅     | `process()` reaches dummy & raises `NotImplementedError` |
| Tests pass                | ✅     | 162 total tests pass           |
| Benchmarks pass           | ✅     | Init time ~0.001ms (< 20ms)    |
| Documentation complete    | ✅     | README in `src/cse/runtime/voice/` |

---

## Verification Results (PRD-005)

| Criterion                 | Status | Detail                         |
|---------------------------|--------|--------------------------------|
| Interface complete        | ✅     | `AcousticBackend` defines strict API |
| Capabilities implemented  | ✅     | `BackendCapabilities` immutable dataclass |
| Registry works            | ✅     | Thread-safe CRUD ops implemented |
| Manager works             | ✅     | Correctly routes initialization |
| Validation works          | ✅     | `validate_before_synthesis` works |
| Tests pass                | ✅     | 16 new tests, all pass |
| Benchmarks pass           | ✅     | Lookup 1000x takes < 1ms (<10ms target)|
| Documentation complete    | ✅     | README in `src/cse/acoustic/backend/`|

---

## Verification Results (PRD-006)

| Criterion                 | Status | Detail                         |
|---------------------------|--------|--------------------------------|
| AudioFrame immutable      | ✅     | Frozen dataclass, generic PCM  |
| Stream works              | ✅     | Lifecycles managed safely      |
| FIFO buffer works         | ✅     | Thread-safe queue wrapper      |
| Controller works          | ✅     | Coordinates stream & buffer    |
| Validation works          | ✅     | Enforces format & duration     |
| Tests pass                | ✅     | 15 new tests, all pass         |
| Benchmarks pass           | ✅     | 1000 pushes/pops in ~2.5ms     |
| Documentation complete    | ✅     | README in `src/cse/streaming/audio/`|

---

## Verification Results (PRD-007)

| Criterion                 | Status | Detail                         |
|---------------------------|--------|--------------------------------|
| Package loads             | ✅     | `PackageLoader` parses dirs    |
| Metadata validates        | ✅     | Strict YAML dictionary checks  |
| Registry works            | ✅     | Thread-safe global registry    |
| Tests pass                | ✅     | 18 tests pass                  |
| Benchmarks pass           | ✅     | Discovery & lookup < 10ms      |
| Documentation complete    | ✅     | README in `src/cse/voice/`     |

---

## Current State (Post PRD-013)
The project validates backend-agnostic architecture through backend capability reporting, dynamic backend switching via the public API (`engine.load_backend`), and standard evaluation prompts. Phase 2 (Infrastructure) is completely proven.

---

## Verification Results (PRD-010)

| Criterion                 | Status | Detail                         |
|---------------------------|--------|--------------------------------|
| CLI works                 | ✅     | `help`, `version`, `voices`, `speak` all work |
| Examples work             | ✅     | 4 runnable examples in `examples/` |
| README updated            | ✅     | Root README completely rewritten |
| Tests pass                | ✅     | CLI tests fully green          |
| Benchmarks pass           | ✅     | Startup is ~0.5ms (target <200ms) |

## Verification Results (PRD-011)

| Criterion                 | Status | Detail                         |
|---------------------------|--------|--------------------------------|
| Package builds            | ✅     | Wheels and sdist build cleanly |
| Entry point works         | ✅     | `cse` CLI installed via scripts |
| Public import works       | ✅     | `from cse import SpeechEngine` works |
| Version exposed           | ✅     | `cse.__version__ == "0.11.0-alpha"` |
| README updated            | ✅     | Quick Start and CLI docs updated |
| Tests pass                | ✅     | All tests green (incl. packaging) |
| Benchmarks pass           | ✅     | Import is ~0.5ms (target <50ms) |

## Verification Results (PRD-012)

| Criterion                 | Status | Detail                         |
|---------------------------|--------|--------------------------------|
| Performance targets met   | ✅     | All subsystems under target    |
| Memory targets met        | ✅     | Idle < 100 MB, import < 50 MB |
| Benchmarks complete       | ✅     | 27 passed, 2 skipped (no model)|
| Regression suite          | ✅     | Threshold assertions on all benchmarks |
| Documentation updated     | ✅     | `docs/Benchmarks/README.md`    |
| Tests pass                | ✅     | Release validation 9/9 green   |

## Verification Results (PRD-013)

| Criterion                 | Status | Detail                         |
|---------------------------|--------|--------------------------------|
| Existing backends work    | ✅     | Kokoro and Dummy function normally |
| Backend switching         | ✅     | `engine.load_backend` works   |
| Capability reporting      | ✅     | `engine.get_backend_capabilities` added |
| Evaluation utilities      | ✅     | `evaluation/compare.py` available |
| Documentation complete    | ✅     | `docs/Backends/README.md` added |
| Tests pass                | ✅     | Backend validation tests green |

## Verification Results (PRD-013.5)

| Criterion                 | Status | Detail                         |
|---------------------------|--------|--------------------------------|
| Fish Speech backend loads | ✅     | `cse.backends.fishspeech` adapter ready |
| StyleTTS2 backend loads   | ✅     | `cse.backends.styletts2` adapter ready |
| Speech generated          | ✅     | Adapters synthesize output |
| Public API unchanged      | ✅     | `engine.load_backend` fully orchestrates |
| Documentation complete    | ✅     | Per-backend READMEs generated |
| Tests pass                | ✅     | Evaluation backend tests pass |

## Verification Results (PRD-013.6)

| Criterion                        | Status | Detail                                     |
|----------------------------------|--------|---------------------------------------------|
| Fish Speech real inference       | ✅     | Verified on Colab                           |
| StyleTTS2 real inference         | ✅     | Verified on Colab                           |
| No placeholder inference remains | ✅     | All dummy WAV headers removed               |
| COLAB-001 updated                | ✅     | Drive mount, Fish Speech v1.5, StyleTTS2    |
| Public API unchanged             | ✅     | No modifications to SpeechEngine/Runtime    |
| Tests pass                       | ✅     | 10/10 local tests green                     |

---

## Verification Results (PRD-014)

| Criterion                 | Status | Detail                         |
|---------------------------|--------|--------------------------------|
| Repository cleaned        | ✅     | Removed placeholders, renamed .benchmarks |
| Documentation complete    | ✅     | ARCHITECTURE, PVD, README, CONTRIBUTING, CHANGELOG, CODE_OF_CONDUCT |
| Installation verified     | ✅     | `pip install -e .` passes      |
| Examples verified         | ✅     | `examples/basic.py` matches PRD |
| Tests pass                | ✅     | 256/256 passing tests          |
| COLAB-001 reproducible    | ✅     | NLTK bug patched, verified by user |
| Real audio generated      | ✅     | Verified in PRD-013.6/COLAB-001 |
| Public API frozen         | ✅     | Version bumped to 1.0.0-beta   |

## Verification Results (PRD-015)

| Criterion                 | Status | Detail                         |
|---------------------------|--------|--------------------------------|
| Backends list voices      | ✅     | Kokoro lists 28, Fish 1, Style 1 |
| Config saves preferences  | ✅     | Written safely via `user_config.py`|
| CLI UI works              | ✅     | `cse voice` interactive select   |
| API falls back gracefully | ✅     | `load_voice()` uses saved config |
| `cse.py` imports fixed    | ✅     | Dropped root `cse.py` script     |

## Verification Results (RELEASE-002 / v1.0.4)

| Criterion                 | Status | Detail                         |
|---------------------------|--------|--------------------------------|
| Packaging                 | ✅     | Scaffold and assets in wheel   |
| Backend self-sufficiency  | ✅     | Asset checks deferred to `speak()` |
| Default voices            | ✅     | StyleTTS2 uses bundled `claire_neutral` |
| Full Kokoro set           | ✅     | 54 voices, 9 languages verified |
| Developer Toolkit         | ✅     | `cse example` & `cse backends` |
| Fish Speech removal       | ✅     | Removed due to env conflicts   |
| Environment stability     | ✅     | Python 3.12+ verified           |

## Verification Results (PRD-016)

| Criterion                 | Status | Detail                         |
|---------------------------|--------|--------------------------------|
| Schema Immutability       | ✅     | `PerformanceContext` frozen dataclass |
| Validation Rules          | ✅     | Rejects empty text             |
| Optional State            | ✅     | Accepts `character_state`      |

## Verification Results (PRD-017)

| Criterion                 | Status | Detail                         |
|---------------------------|--------|--------------------------------|
| Sequential Execution      | ✅     | `ReasoningPipeline` tests pass |
| Input Validation          | ✅     | Rejects invalid context        |

## Verification Results (PRD-018)

| Criterion                 | Status | Detail                         |
|---------------------------|--------|--------------------------------|
| Immutability              | ✅     | `PerformanceRepresentation` frozen dataclass |
| Data Preservation         | ✅     | Preserves `text` and `character_state` |
| Input Validation          | ✅     | Rejects states missing `text`  |

## Verification Results (PRD-019)

| Criterion                 | Status | Detail                         |
|---------------------------|--------|--------------------------------|
| Interface Base            | ✅     | `BaseTranslator` ABC defined   |
| Input Validation          | ✅     | Validates `PerformanceRepresentation` in `process()` |
| Backend Independence      | ✅     | No backend-specific logic      |
