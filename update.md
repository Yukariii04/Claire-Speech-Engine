# Claire Speech Engine â€” Update Log

> Evolutionary history from initial commit to present.

---

## 2026-07-06 â€” Project Inception

- **PRD-001.md** added to workspace â€” defines the bootstrap & foundation milestone.
- **memory.md** created â€” stores architecture context, lore, and active state.
- **update.md** created â€” this file; tracks all project history.

## 2026-07-06 â€” PRD-001 Implementation

### Phase 1: Scaffold
- Created all base files: `pyproject.toml`, `requirements.txt`, `.gitignore`, `.editorconfig`, `.pre-commit-config.yaml`, `LICENSE`
- Created `configs/default.yaml` with engine name/version and runtime debug flag
- Created directory structure with `.gitkeep` placeholders for all 14 top-level dirs

### Phase 2: Core Systems
- **Config system** (`src/cse/config/manager.py`): YAML loading, dotted-key access, `CSE_` env-var overrides, validation, hot-reload via `reload()`
- **Logger** (`src/cse/core/logger.py`): loguru-based, colorized stderr, timestamped, configurable debug level
- **Module registry** (`src/cse/core/registry.py`): register/get/list/is_registered, duplicate protection
- **Plugin base** (`src/cse/plugins/base.py`): ABC with `initialize()`, `shutdown()`, `metadata()`

### Phase 3: Runtime & Entry Point
- **Bootstrap** (`src/cse/runtime/bootstrap.py`): linear boot sequence with argparse CLI (`--help`, `--version`, `--debug`), Rich console banner
- **Entry point** (`cse.py`): `__main__`-guarded, sys.path swap to resolve package from `src/`
- **Top-level package** (`src/cse/__init__.py`): exports 5 public API functions

### Phase 4: Tests & Benchmarks
- 5 test files, 24 real tests covering config, logger, registry, bootstrap, CLI
- 1 benchmark: bootstrap startup timing (mean 2.08 ms, target < 300 ms)
- `conftest.py`: force-loads cse package via importlib to avoid cse.py shadowing

### Phase 5: Documentation
- `README.md` with Installation, Project Goals, Repository Structure, Running, Development, Contributing

### Bug Fixes
- Fixed `pyproject.toml` build-backend (`setuptools.backends._legacy` â†’ `setuptools.build_meta`)
- Fixed `cse.py` name collision with `cse` package (module-level code â†’ `__main__` guard + sys.path swap)
- Fixed pytest import resolution via `conftest.py` force-loading the package with `importlib.util`

### Verification
All 8 PRD-001 acceptance criteria passed:
- âœ… Project installs (`pip install -e ".[dev]"`)
- âœ… Runtime starts (exact banner match)
- âœ… Runtime shuts down cleanly
- âœ… Logger works (all 5 levels)
- âœ… Configuration loads (YAML, env overrides, validation, reload)
- âœ… Tests pass (24/24)
- âœ… Benchmarks execute (2.08 ms mean, well under 300 ms)
- âœ… Documentation complete

## 2026-07-06 â€” PRD-002 Implementation (CIR)

### Phase 1: Foundation (TDD)
- Created `exceptions.py` with 3 typed error classes.
- Created `ids.py` for deterministic UUID5 generation using a CIR namespace.
- Created `schema.py` defining the immutable CIR object hierarchy (`CIRDocument`, `CIRUtterance`, `CIRSpeechSegment`, `CIRLexicalToken`) using frozen dataclasses and tuples.
- Wrote failing unit tests for schema, exceptions, and IDs.

### Phase 2: Core Components (TDD)
- Wrote failing unit tests for Builder, Validator, Serializer, and Public API (93 tests total).
- Implemented `builder.py` to parse text into sentences, segments, and tokens with deterministic UUIDs and precise source offsets.
- Implemented `validator.py` to enforce strict structural integrity (version, hierarchy, non-empty, unique UUIDs).
- Implemented `serializer.py` for lossless JSON round-trip serialization.
- Implemented `parser.py` as a semantic alias for `build_cir`.
- Exposed the public API in `cir/__init__.py`.
- Fixed a bug where identical sentences produced duplicate UUIDs by mixing `source_offset` into the UUID seed.

### Phase 3: Benchmarks & Documentation
- Wrote benchmarks validating that 100-word paragraph builds take < 5 ms (actual: 0.65 ms) and 1000 builds take < 1 second (actual: 35 ms).
- Added `README.md` in `src/cse/language/cir/` explaining the architecture, API, and purpose of CIR.

### Verification
All PRD-002 acceptance criteria passed:
- âœ… Immutable (Frozen dataclasses, tuple fields)
- âœ… Serializable (Lossless JSON round-trip)
- âœ… Versioned (`CIR_VERSION = "2.0.0"`)
- âœ… UUIDs implemented (Deterministic UUID5)
- âœ… Validation works (Catch duplicate UUIDs, malformed hierarchies)
- âœ… Benchmarks pass (Builder: 0.65ms, 1000 builds: 35ms)
- âœ… Tests pass (117/117 passed)
- âœ… Documentation complete (README added)
- âœ… Public API stable (5 functions only)

## 2026-07-06 â€” PRD-003 Implementation (Performance Compiler)

### Phase 1: Foundation (TDD)
- Evaluated AI Skills and noted `ponytail` as highly applicable to keep implementation minimal without anticipating future PRDs.
- Created `exceptions.py` with 3 typed error classes.
- Created `events.py` and `timeline.py` for the immutable Performance Timeline schema and event definitions.
- Wrote failing unit tests for schema and exceptions.

### Phase 2: Core Components (TDD)
- Implemented `compiler.py` to compile CIR into an ordered timeline with `SPEAK_START`, `TOKEN`, and `SPEAK_END` events. Tokens default to `0.5` for all attributes and strictly `150ms` duration.
- Implemented `validator.py` for structural checks (negative timestamps, event order, parameters out of bounds, duplicate UUIDs).
- Implemented `serializer.py` for lossless JSON round-tripping.
- Added `tests/golden/test_perf_golden.py` to assert the timeline exact structure against the PRD example.
- Exposed the public API in `compiler/__init__.py`.

### Phase 3: Benchmarks & Documentation
- Added benchmarks ensuring compilation takes < 2 ms and 1000 timelines are built in < 1s.
- Created `README.md` explaining the Timeline structure, API, and current limitations.

### Verification
All PRD-003 acceptance criteria passed:
- âœ… Timeline builds
- âœ… Events generated (Start, Token, End)
- âœ… Validation works (Timestamps, parameters, order)
- âœ… Serialization works (JSON round-trip)
- âœ… Benchmarks pass (100-word: ~0.5ms, 1000 builds: ~20ms)
- âœ… Golden tests pass
- âœ… API documented
- âœ… Thread safe (Stateless)
- âœ… Immutable (Frozen dataclasses, tuples)

## 2026-07-06 â€” PRD-004 Implementation (Voice Runtime)

### Phase 1: Foundation (TDD)
- Evaluated AI Skills and noted `ponytail` as highly applicable to keep orchestration purely structural, strictly avoiding synthesis, streaming, and fake audio.
- Initializing directory structure `src/cse/runtime/voice/`.

### Phase 2: Core Components (TDD)
- Implemented `state.py` containing the `RuntimeState` enum enforcing the state machine.
- Implemented `exceptions.py` with specific error classes (e.g. `InvalidRuntimeStateError`, `VoiceNotFoundError`).
- Implemented `backend.py` with `AcousticBackend` interface and a `DummyBackend` that satisfies initialization but raises `NotImplementedError` upon synthesis.
- Implemented `manager.py` that discovers and loads YAML `metadata.yaml` for voices without loading heavy models.
- Implemented `runtime.py` (`VoiceRuntime`) which handles orchestration and strict state transitions.

### Phase 3: Benchmarks & Documentation
- Validated performance: initialization takes ~0.001ms (target < 20ms).
- Created `README.md` explaining the orchestration boundaries.

### Verification
All PRD-004 acceptance criteria passed:
- âœ… Runtime initializes
- âœ… Voice metadata loads
- âœ… Runtime state transitions work
- Implemented `capabilities.py`, `exceptions.py`, `interface.py`, and `dummy_backend.py`.
- Implemented `registry.py` for thread-safe backend registration.
- Implemented `manager.py` to handle backend initialization and lifecycle.
- Implemented `validator.py` to ensure state is valid before synthesis.
- Refactored `VoiceRuntime` to use the new `cse.acoustic.backend` package as the single source of truth, safely removing the previous placeholder.

### Phase 3: Benchmarks & Documentation
- Validated performance: 1000 backend lookups take ~0.23ms (target < 10ms).
- Created `README.md` defining the backend abstraction architecture.

### Verification
All PRD-005 acceptance criteria passed:
- âœ… Registry works
- âœ… Manager works
- âœ… Interface complete
- âœ… Capabilities implemented
- âœ… Validation works
- âœ… Tests pass
- âœ… Benchmarks pass
- âœ… Documentation complete

## 2026-07-06 â€” PRD-006 Implementation (Audio Streaming Pipeline)

### Phase 1: Foundation (TDD)
- Evaluated AI Skills: `ponytail` enforces a strictly internal data structure with zero actual I/O, networking, or playback. Frames remain immutable and PCM agnostic.
- Initializing directory structure `src/cse/streaming/audio/`.

### Phase 2: Core Components (TDD)
- Implemented `frame.py` with immutable, PCM-agnostic `AudioFrame` structure.
- Implemented `stream.py` to containerize frames.
- Implemented `buffer.py` providing a thread-safe FIFO queue for both blocking and non-blocking reads.
- Implemented `controller.py` to own stream lifecycles.
- Implemented `validator.py` ensuring positive rates, valid channels, and stream constraints.
- Implemented `serializer.py` with base64/JSON hooks for wire transport.

### Phase 3: Benchmarks & Documentation
- Validated performance: 1000 pushes and pops take ~2.5ms (target < 20ms).
- Created `README.md` defining the streaming architecture constraints.

### Verification
All PRD-006 acceptance criteria passed:
- âœ… AudioFrame immutable
- âœ… Stream works
- âœ… FIFO buffer works
- âœ… Controller works
- âœ… Validation works
- âœ… Tests pass
- âœ… Benchmarks pass
- âœ… Documentation complete

## 2026-07-06 â€” PRD-007 Implementation (Voice Package System)

### Phase 1: Foundation (TDD)
- Evaluated AI Skills: `ponytail` enforces a strictly metadata-only package system with no Torch, ONNX, or inference logic. We will establish the `cse.voice` package and refactor the PRD-004 `VoiceRuntime` to use it as the single source of truth for voices.
- Initializing directory structure `src/cse/voice/`.

### Phase 2: Core Components (TDD)
- Implemented `metadata.py` and `package.py` to define the immutable `VoicePackage` structure.
- Implemented `validator.py` to enforce required YAML schema fields.
- Implemented `loader.py` for stateless directory ingestion and YAML parsing.
- Implemented `registry.py` providing a thread-safe, global singleton repository for loaded packages.
- Refactored `VoiceRuntime` to utilize the new `cse.voice` package instead of the primitive `VoiceManager`.
- Deleted the obsolete PRD-004 `VoiceManager`.

### Phase 3: Benchmarks & Documentation
- Validated performance: Package discovery and metadata loading takes ~0.64ms (< 10ms). 1000 lookups take ~0.31ms (< 10ms).
- Created `README.md` defining the voice package philosophy and layout.

### Verification
All PRD-007 acceptance criteria passed:
- âœ… Package loads
- âœ… Metadata validates
- âœ… Registry works
- âœ… Tests pass
- âœ… Benchmarks pass
- âœ… Documentation complete

## 2026-07-07 â€” PRD-008 Implementation (Kokoro Backend)

### Phase 1: Foundation
- Evaluated AI Skills: `ponytail` enforces a thin adapter pattern â€” only `backends/kokoro/` imports Kokoro. The rest of CSE is completely unaware Kokoro exists. No architecture modifications.
- Initializing directory structure `src/cse/backends/kokoro/`.

### Phase 2: Core Components
- Implemented `config.py` â€” immutable `KokoroConfig` with model paths, voice defaults, and output settings.
- Implemented `exceptions.py` â€” `KokoroInitializationError`, `VoiceLoadError`, `SpeechGenerationError` hierarchy.
- Implemented `converter.py` â€” `timeline_to_text()` extracts only TOKEN events, ignoring emphasis/pauses/breathing per PRD-008 Â§9.
- Implemented `loader.py` â€” `resolve_voice()` maps voice names to Kokoro identifiers.
- Implemented `result.py` â€” immutable `SpeechResult` frozen dataclass with all required fields.
- Implemented `backend.py` â€” `KokoroBackend(AcousticBackend)` with full lifecycle: initialize â†’ load_voice â†’ synthesize â†’ shutdown.
- Kokoro-specific imports (`kokoro_onnx`, `soundfile`) confined exclusively to `backends/kokoro/`.

### Phase 3: Tests & Benchmarks
- 19 tests: 18 unit tests (mocked Kokoro) + 1 integration test (real model).
- Unit tests cover: exceptions, config, converter, loader, SpeechResult, backend init/shutdown/synthesize/validate.
- Integration test validates full lifecycle with real Kokoro model files.
- Benchmarks: Converter 1000x in ~279Î¼s, mocked synthesis ~2.4ms, real Kokoro warm synthesis ~777ms.

### Phase 4: Documentation
- Created `README.md` in `src/cse/backends/kokoro/` covering installation, dependencies, lifecycle, configuration, and known limitations.

### Bug Fix: Corrupted Voices File
- `voices-v1.0.bin` was truncated (24.8 MB vs expected 28.2 MB), causing `BadZipFile` during `np.load()`.
- Re-downloaded from GitHub releases to correct 28,214,398 bytes. Integration test now passes.

### Verification
All PRD-008 acceptance criteria passed:
- âœ… Backend initializes (Kokoro ONNX pipeline)
- âœ… Voice loads (`load_voice()` resolves names)
- âœ… Speech generated (real Kokoro synthesis)
- âœ… WAV saved (UUID-named in `temp/`)
- âœ… SpeechResult returned (immutable frozen dataclass)
- âœ… Tests pass (19/19, 213 total project-wide)
- âœ… Benchmarks pass (warm synthesis ~777ms, target <1.5s)
- âœ… Documentation complete (README in `src/cse/backends/kokoro/`)

### Architecture Validation
PRD-008 proves the CSE architecture is genuinely backend-agnostic:
- Only `backends/kokoro/` imports Kokoro-specific libraries
- The rest of CSE remains completely unaware Kokoro exists
- Deleting `backends/kokoro/` and adding `backends/claire/` would require zero changes to the core

## 2026-07-07 â€” PRD-009 Implementation (Public Speech Engine API)

### Phase 1: Foundation
- Evaluated AI Skills: `ponytail` enforces a minimal facade pattern. No extra logic, just strict delegation.
- Created `src/cse/api/` with `engine.py`, `config.py`, `lifecycle.py`, and `exceptions.py`.

### Phase 2: Core Components
- `SpeechEngine` class implemented to handle initialization, configuration loading, voice loading, and speech generation pipeline.
- `EngineConfig` implemented to standardize overrides.
- Refactored `src/cse/__init__.py` to export **only** the `SpeechEngine` class, strictly encapsulating all other modules as internal details per PRD-009 Â§17.

### Phase 3: Tests & Benchmarks
- 14 API unit tests verify initialization, voice loading, speech generation, and lifecycle idempotency.
- Benchmarks show Engine Creation overhead at ~1.6Âµs (<100ms target) and Speech Request overhead at ~134Âµs (<10ms target).

### Phase 4: Documentation
- Created `src/cse/api/README.md` with Quick Start examples and lifecycle explanations.

### Verification
- âœ… Engine initializes
- âœ… Voice loads
- âœ… Speech generates
- âœ… SpeechResult returned
- âœ… Shutdown works
- âœ… Tests pass (14/14)
- âœ… Benchmarks pass
- âœ… Documentation complete

## 2026-07-07 â€” PRD-010 Implementation (Developer Experience)

### Phase 1: Foundation
- Evaluated AI Skills: `ponytail` enforced a minimalist approach to the CLI. We relied strictly on `argparse` from the standard library to avoid bloat and third-party dependencies like `click`.

### Phase 2: Core Components
- Created `examples/` directory containing four runnable examples (`basic.py`, `configuration.py`, `list_voices.py`, `generate_speech.py`).
- Implemented `src/cse/cli/` using `argparse` to provide `help`, `version`, `voices`, and `speak` commands.
- Redirected root `cse.py` to use the new CLI instead of the internal bootstrap loader.

### Phase 3: Tests & Benchmarks
- Updated `tests/test_cli.py` to cover all new CLI commands and edge cases.
- CLI startup benchmark achieved `~0.5ms` (target `<200ms`), by lazy-loading `SpeechEngine` only when required.

### Phase 4: Documentation
- Rewrote the root `README.md` to focus on the Developer Experience (What is CSE, Quick Start, Examples).
- Added `README.md` to `src/cse/cli/`.

### Verification
- âœ… CLI works
- âœ… Examples work
- âœ… README updated
- âœ… Tests pass (8/8 CLI tests)
- âœ… Benchmarks pass (~0.5ms)

## 2026-07-07 â€” PRD-011 Implementation (Release Architecture & Packaging)

### Phase 1: Configuration
- Reconfigured `pyproject.toml` to support `build` metadata, identifying dependencies and adding an explicit `project.scripts` mapping for `cse = "cse.cli.main:main"`.
- Set package version to `"0.11.0-alpha"`.

### Phase 2: Imports & Documentation
- Edited `src/cse/__init__.py` to expose `SpeechEngine` and `__version__`.
- Updated `README.md` to properly feature the PyPI-esque installation path alongside the Python API.

### Phase 3: Tests & Validation
- Wrote `tests/test_packaging.py` validating that the entry point `cse` commands return correctly, the version is properly formatted, the package builds, and the public import works.
- Wrote `benchmarks/test_import_time.py` to ensure imports take `< 50ms`. Actual time: `~0.5ms`.

### Verification
- âœ… Package builds
- âœ… Entry point works
- âœ… Public import works
- âœ… Version exposed
- âœ… README updated
- âœ… Tests pass

## 2026-07-07 â€” PRD-012 Implementation (Performance Optimization & Release Validation)

### Phase 1: Regression Thresholds
- Added threshold assertions to all existing benchmarks missing them: `test_cli.py` (< 200ms), `test_api_engine.py` (< 100ms creation, < 10ms overhead), `test_import_time.py` (< 50ms).

### Phase 2: Memory Profiling
- Created `benchmarks/test_memory.py` using stdlib `tracemalloc` (ponytail: no psutil dependency). Validates engine idle < 100 MB and import < 50 MB.

### Phase 3: Release Validation
- Created `tests/test_release_validation.py` verifying all release assets: README sections, LICENSE, pyproject metadata, examples, requirements, package build, public import, version string, CLI entry point.

### Phase 4: Documentation
- Created `docs/Benchmarks/README.md` with performance targets, measured results, regression threshold map, running instructions, and optimization notes.

### Verification
- âœ… Performance targets met (all subsystems under target)
- âœ… Memory targets met (idle < 100 MB, import < 50 MB)
- âœ… Benchmarks complete (27 passed, 2 skipped â€” no Kokoro model files)
- âœ… Regression suite implemented (threshold assertions on all benchmarks)
- âœ… Documentation updated (`docs/Benchmarks/`)
- âœ… Tests pass (release validation 9/9 green)

## 2026-07-07 â€” PRD-013 Implementation (Multi-Backend Validation)

### Phase 1: Capability Reporting
- Added `backend_name`, `emotion`, and `sample_rate` to `BackendCapabilities`.
- Updated `DummyBackend` and `KokoroBackend` to report these capabilities.

### Phase 2: Backend Switching
- Added `load_backend` and `get_backend_capabilities` to the public `SpeechEngine` and `VoiceRuntime` to allow dynamic switching without changing the API contract.

### Phase 3: Evaluation Utilities
- Created `evaluation/prompts/standard.txt` containing 8 diverse evaluation prompts.
- Created `evaluation/compare.py` to iterate through available backends and generate side-by-side synthesis outputs (or intentionally skip missing evaluation backends like Fish Speech).

### Phase 4: Documentation & Tests
- Added `docs/Backends/README.md` to document the switching workflow and capability reporting.
- Created `tests/test_backend_validation.py` to verify API routing and capability structure.

### Verification
- âœ… Existing backends remain functional (Dummy, Kokoro)
- âœ… Backend switching works (`engine.load_backend()`)
- âœ… Capability reporting implemented (`engine.get_backend_capabilities()`)
- âœ… Evaluation utilities available (`evaluation/compare.py`)
- âœ… Documentation complete (`docs/Backends/README.md`)
- âœ… Tests pass (backend validation tests green)

## 2026-07-07 â€” COLAB-001 (Engineering Validation Notebook)

### Phase 1: Notebook Construction
- Generated `docs/Notebooks/COLAB-001.ipynb`.
- Constructed strictly as an engineering validation test (no expressiveness benchmarking yet).
- Includes cells for environment setup, CSE installation from Git, dummy/fishspeech backend loading via the public API, audio generation, and output verification.
- Validates the backend abstraction and API contract in a remote Colab environment.

## 2026-07-07 â€” PRD-013.5 Implementation (Evaluation Backend Integration)

### Phase 1: Backend Adapters
- Scaffolded standard AcousticBackend adapters for `fishspeech` and `styletts2` inside `src/cse/backends/`.
- Included capability declarations independent of core engine features (Fish Speech: `emotion="high"`, StyleTTS2: `emotion="medium"`).
- Adapted `VoiceRuntime.load_backend` to properly lazily-route to these new adapters.

### Phase 2: Tests & Documentation
- Scaffolded `README.md` and standard directory structures for both backends.
- Created `tests/test_evaluation_backends.py` achieving 100% pass rate for standalone instantiation and engine-routed orchestration.

### Verification
- âœ… Fish Speech backend loads
- âœ… StyleTTS2 backend loads
- âœ… Speech generated (adapter stubs successfully emit mock wav output)
- âœ… Public API unchanged
- âœ… Documentation complete
- âœ… Tests pass

## 2026-07-10 â€” PRD-013.6 Implementation (Real Evaluation Backend Completion)

### Changes
- Replaced placeholder Fish Speech backend with real 3-stage subprocess inference pipeline (VQ encode â†’ LLM generate â†’ VQ decode), reused directly from `claire_colab.ipynb`.
- Replaced placeholder StyleTTS2 backend with real inference via the `styletts2` Python package API.
- Both backends now extract text from `PerformanceTimeline` TOKEN events using the existing `timeline_to_text` converter.
- Fish Speech backend reads reference audio from Google Drive (`/content/drive/MyDrive/claire/voices/`), matching the Claire2D workflow.
- Updated COLAB-001 notebook: Drive mount, Fish Speech v1.5 installation with dependency patching, StyleTTS2 installation, real speech generation for both backends, audio download.
- Updated tests to 10/10 pass (local validation without GPU; real inference validated via COLAB-001).

### Verification (verified on Colab)
- âœ… Fish Speech produces real audible speech
- âœ… StyleTTS2 produces real audible speech
- âœ… No placeholder inference remains
- âœ… Public API unchanged
- âœ… Tests pass (10/10)

## 2026-07-10 â€” PRD-014 (v1.0.0-beta Readiness)

### Goal
Certify the framework is ready to become v1.0.0-beta. Stop adding framework features and focus entirely on release engineering: stability, documentation, reproducibility, and contributor experience.

### Plan
1. **Repository Cleanup**: Rename `.benchmarks` to `benchmarks`, remove unused placeholder directories.
2. **Documentation**: Verify/create `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`, `LICENSE`, `CODE_OF_CONDUCT.md`.
3. **Architecture Docs**: Create `docs/Architecture/ARCHITECTURE.md`.
4. **Vision Docs**: Create `docs/PVDs/PVD-001.md`.
5. **Examples**: Add a clear end-to-end example.
6. **COLAB-001 Verification**: Verify it still works perfectly for both backends.
7. **Packaging & Testing**: Verify pip installability, run full test suite.
8. **Final Tag**: Cut `v1.0.0-beta`.

## 2026-07-10 — RELEASE-001 (v1.0.0-beta Publish)

### Goal
Publish the Claire Speech Engine as a real installable Python package on TestPyPI and PyPI. No framework changes — pure release engineering.

### Plan
1. Review and fix `pyproject.toml` metadata (classifiers, URLs, long_description).
2. Build wheel and sdist via `python -m build`.
3. Validate with `twine check dist/*`.
4. Upload to TestPyPI, verify `pip install` from TestPyPI.
5. Upload to PyPI.
6. Fresh environment validation.
7. Update COLAB-001 to install from PyPI.
8. Publish GitHub Release with assets.
9. Update README installation instructions.

## 2026-07-12 — PRD-015 Implementation (Voice Discovery & Interactive CLI)

### Phase 1: Core API & Backend Integration
- Abstracted voice logic in `AcousticBackend` with `list_voices()` and `validate_voice()`.
- Implemented `Kokoro` backend discovery returning all 28 ONNX voices natively.
- Implemented `FishSpeech` backend discovery dynamically recursively finding any `.wav` file anywhere in the codebase (ignoring temp/venv) to register as a zero-shot reference voice.
- Implemented `StyleTTS2` backend discovery returning a basic `default` voice.
- Refactored `VoiceRuntime` to delegate voice loading and validation to backends, bypassing the legacy `VoicePackage` boilerplate.

### Phase 2: Configuration & Persistence
- Created `src/cse/config/user_config.py` using standard OS paths to save CLI-level preferences persistently across runs.
- Configured `Engine.load_voice()` to automatically pull from `user_config` when called without arguments.

### Phase 3: Interactive CLI
- Developed `cse voices` to universally display all available voices grouped by backend.
- Developed `cse voice` (interactive selection), `cse voice set`, `cse voice current`, and `cse voice reset`.
- Removed `cse.py` and relied purely on `pyproject.toml`'s entry_points, solving import collisions.

### Phase 4: Script & README Refactoring
- Removed legacy `register_voice_package` hacks from `interactive_kokoro.py` and `interactive_fish.py`, updating them to leverage zero-arg `engine.load_voice()`.
- Updated `README.md` and `src/cse/cli/README.md` to reflect the new UI paradigm.
- Generated `ClaireSpeechEngine-PRD015.zip`.

### Verification
- ✅ CLI voice config saves persistently.
- ✅ Backends enumerate voices correctly.
- ✅ Python API falls back to user preferences seamlessly.
- ✅ Tests pass (discovery and routing verified).
- ✅ Import issues fixed (`cse.py` collision resolved).

---

## RELEASE-002 — v1.0.4 (2026-07-13)

### §1a: Backend Self-Sufficiency
- Deferred asset checks from `initialize()` to first `synthesize()` for FishSpeech and Kokoro.
- StyleTTS2 already had this pattern (`_ensure_model()`) — FishSpeech and Kokoro now match.
- `initialize()` across all 3 backends is now lightweight (import check only).

### §1b: FishSpeech Default Voice
- Moved `claire_neutral.wav` from repo root → `src/cse/backends/fishspeech/assets/`.
- Bundled asset always injected as baseline in `_scan_for_wavs()`; project-level wav overrides.
- Deterministic fallback: unknown voice falls back to `claire_neutral` with logged warning.
- Missing bundled asset raises a clear "broken install" error, never an arbitrary wav.

### §1c: StyleTTS2 Thread Safety + Default Voice
- Added module-level `threading.Lock()` around `_ensure_model()` torch.load monkeypatch.
- Double-check pattern after lock acquisition.
- Reuses bundled `claire_neutral.wav` from fishspeech assets as default reference.
- `list_voices()` now reports `claire_neutral` instead of generic `default`.

### §1d: Kokoro Full Voice Set
- Replaced 28-voice English-only list with full 54-voice set across 9 languages.
- Verified against `hexgrad/Kokoro-82M` VOICES.md on Hugging Face.
- Fixed `am_fable` → `am_fenrir` bug from v1.0.2.
- Updated `supported_languages` from `("en",)` to `("en", "ja", "zh", "es", "fr", "hi", "it", "pt")`.
- Added comments noting Japanese/Mandarin require `misaki[ja]`/`misaki[zh]` for G2P.

### §2: Developer Toolkit
- Created `src/cse/_scaffold/` with 3 example scripts + README.
- `cse example` copies all scripts into cwd; `cse example <backend>` copies just one.
- `cse backends` shows a health dashboard per backend (status, voices, languages).
- All scaffold files ship inside the wheel via `package_data`.

### §3: Packaging
- Version bumped 1.0.2 → 1.0.4.
- `pyproject.toml` `package-data` includes `backends/fishspeech/assets/*.wav` and `_scaffold/*`.

### §4-5: Build + Twine Verification
- ✅ Wheel builds, contains all voice assets + scaffold files.
- ✅ `twine check dist/*` passes.

### Fish Speech Removal (1.0.4 pivot)
- Discovered severe environment conflicts between `FishSpeech` dependencies (`torch<=2.4.1`, `torchaudio`, `pytorch-lightning`, outdated `transformers`) and modern Python 3.12+ setups on Windows.
- PyTorch C++ extension mismatch (`[WinError 127]`) made it impossible to maintain a unified, stable environment for Kokoro, StyleTTS2, and Fish Speech.
- **Decision**: Removed `cse.backends.fishspeech`, removed `cse setup fishspeech`, and purged `example_fishspeech.py` from the scaffold.
- Reverted `claire-speech-engine` constraints back to `requires-python = ">=3.12"`.
- Documented in `memory.md` (AD-003) and `README.md`.

### Completion (v1.0.4)
- ✅ Local install dry run passed in fresh Python 3.12+ environment (`cse` env).
- ✅ Wheel rebuilt and tested successfully.
- ✅ Fish Speech fully excised; `claire_neutral` migrated correctly to `styletts2`.
- ✅ All acceptance criteria met (excluding PyPI publish which is left for user manual action if desired).
- ✅ RELEASE-002 completed and repository zipped.

## 2026-07-15 — PRD-016 Implementation (Performance Context)

- **PRD-016** implemented utilizing Ponytail rules (simplest path, standard library only).
- Created `PerformanceContext` in `src/cse/performance/context.py` using `dataclasses.dataclass(frozen=True)`.
- Enforced mandatory `text` and optional `character_state` with runtime check in `__post_init__`.
- Added test file `tests/test_perf_context.py` to verify schema, immutability, and validation.
- All tests passing. Zipped as `ClaireSpeechEngine-PRD016.zip`.

## 2026-07-15 — PRD-017 Implementation (Reasoning Pipeline)

- **PRD-017** implemented utilizing Ponytail rules (simplest path).
- Created `ReasoningPipeline` orchestrator in `src/cse/performance/pipeline.py`.
- Accepts `PerformanceContext` and executes an arbitrary sequence of functional stages.
- Validates input is exactly a `PerformanceContext`.
- Added `tests/test_perf_pipeline.py` testing sequential execution and validation.
- All tests passing. Zipped as `ClaireSpeechEngine-PRD017.zip`.

## 2026-07-15 — PRD-018 Implementation (Performance Representation Builder)

- **PRD-018** implemented utilizing Ponytail rules (simplest path).
- Created `PerformanceRepresentation` frozen dataclass in `src/cse/performance/representation.py`.
- Created `build_performance_representation()` in `src/cse/performance/builder.py`.
- Enforced validation logic to ensure pipeline output contains the required fields before construction.
- Added `tests/test_perf_representation.py` testing immutability and valid/invalid state conversions.
- All tests passing. Zipped as `ClaireSpeechEngine-PRD018.zip`.

## 2026-07-15 — PRD-019 Implementation (Translator Interface)

- **PRD-019** implemented utilizing Ponytail rules (simplest path).
- Created `BaseTranslator` abstract base class in `src/cse/performance/translator.py`.
- Integrated input validation directly into the base class `process()` method to guarantee all derived translators strictly receive a valid `PerformanceRepresentation`.
- Added `tests/test_perf_translator.py` testing successful processing and rejection of invalid inputs.
- All tests passing. Zipped as `ClaireSpeechEngine-PRD019.zip`.
