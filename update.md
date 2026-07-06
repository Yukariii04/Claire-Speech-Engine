# Claire Speech Engine — Update Log

> Evolutionary history from initial commit to present.

---

## 2026-07-06 — Project Inception

- **PRD-001.md** added to workspace — defines the bootstrap & foundation milestone.
- **memory.md** created — stores architecture context, lore, and active state.
- **update.md** created — this file; tracks all project history.

## 2026-07-06 — PRD-001 Implementation

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
- Fixed `pyproject.toml` build-backend (`setuptools.backends._legacy` → `setuptools.build_meta`)
- Fixed `cse.py` name collision with `cse` package (module-level code → `__main__` guard + sys.path swap)
- Fixed pytest import resolution via `conftest.py` force-loading the package with `importlib.util`

### Verification
All 8 PRD-001 acceptance criteria passed:
- ✅ Project installs (`pip install -e ".[dev]"`)
- ✅ Runtime starts (exact banner match)
- ✅ Runtime shuts down cleanly
- ✅ Logger works (all 5 levels)
- ✅ Configuration loads (YAML, env overrides, validation, reload)
- ✅ Tests pass (24/24)
- ✅ Benchmarks execute (2.08 ms mean, well under 300 ms)
- ✅ Documentation complete

## 2026-07-06 — PRD-002 Implementation (CIR)

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
- ✅ Immutable (Frozen dataclasses, tuple fields)
- ✅ Serializable (Lossless JSON round-trip)
- ✅ Versioned (`CIR_VERSION = "2.0.0"`)
- ✅ UUIDs implemented (Deterministic UUID5)
- ✅ Validation works (Catch duplicate UUIDs, malformed hierarchies)
- ✅ Benchmarks pass (Builder: 0.65ms, 1000 builds: 35ms)
- ✅ Tests pass (117/117 passed)
- ✅ Documentation complete (README added)
- ✅ Public API stable (5 functions only)

## 2026-07-06 — PRD-003 Implementation (Performance Compiler)

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
- ✅ Timeline builds
- ✅ Events generated (Start, Token, End)
- ✅ Validation works (Timestamps, parameters, order)
- ✅ Serialization works (JSON round-trip)
- ✅ Benchmarks pass (100-word: ~0.5ms, 1000 builds: ~20ms)
- ✅ Golden tests pass
- ✅ API documented
- ✅ Thread safe (Stateless)
- ✅ Immutable (Frozen dataclasses, tuples)

## 2026-07-06 — PRD-004 Implementation (Voice Runtime)

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
- ✅ Runtime initializes
- ✅ Voice metadata loads
- ✅ Runtime state transitions work
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
- ✅ Registry works
- ✅ Manager works
- ✅ Interface complete
- ✅ Capabilities implemented
- ✅ Validation works
- ✅ Tests pass
- ✅ Benchmarks pass
- ✅ Documentation complete

## 2026-07-06 — PRD-006 Implementation (Audio Streaming Pipeline)

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
- ✅ AudioFrame immutable
- ✅ Stream works
- ✅ FIFO buffer works
- ✅ Controller works
- ✅ Validation works
- ✅ Tests pass
- ✅ Benchmarks pass
- ✅ Documentation complete

## 2026-07-06 — PRD-007 Implementation (Voice Package System)

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
- ✅ Package loads
- ✅ Metadata validates
- ✅ Registry works
- ✅ Tests pass
- ✅ Benchmarks pass
- ✅ Documentation complete

## 2026-07-07 — PRD-008 Implementation (Kokoro Backend)

### Phase 1: Foundation
- Evaluated AI Skills: `ponytail` enforces a thin adapter pattern — only `backends/kokoro/` imports Kokoro. The rest of CSE is completely unaware Kokoro exists. No architecture modifications.
- Initializing directory structure `src/cse/backends/kokoro/`.

### Phase 2: Core Components
- Implemented `config.py` — immutable `KokoroConfig` with model paths, voice defaults, and output settings.
- Implemented `exceptions.py` — `KokoroInitializationError`, `VoiceLoadError`, `SpeechGenerationError` hierarchy.
- Implemented `converter.py` — `timeline_to_text()` extracts only TOKEN events, ignoring emphasis/pauses/breathing per PRD-008 §9.
- Implemented `loader.py` — `resolve_voice()` maps voice names to Kokoro identifiers.
- Implemented `result.py` — immutable `SpeechResult` frozen dataclass with all required fields.
- Implemented `backend.py` — `KokoroBackend(AcousticBackend)` with full lifecycle: initialize → load_voice → synthesize → shutdown.
- Kokoro-specific imports (`kokoro_onnx`, `soundfile`) confined exclusively to `backends/kokoro/`.

### Phase 3: Tests & Benchmarks
- 19 tests: 18 unit tests (mocked Kokoro) + 1 integration test (real model).
- Unit tests cover: exceptions, config, converter, loader, SpeechResult, backend init/shutdown/synthesize/validate.
- Integration test validates full lifecycle with real Kokoro model files.
- Benchmarks: Converter 1000x in ~279μs, mocked synthesis ~2.4ms, real Kokoro warm synthesis ~777ms.

### Phase 4: Documentation
- Created `README.md` in `src/cse/backends/kokoro/` covering installation, dependencies, lifecycle, configuration, and known limitations.

### Bug Fix: Corrupted Voices File
- `voices-v1.0.bin` was truncated (24.8 MB vs expected 28.2 MB), causing `BadZipFile` during `np.load()`.
- Re-downloaded from GitHub releases to correct 28,214,398 bytes. Integration test now passes.

### Verification
All PRD-008 acceptance criteria passed:
- ✅ Backend initializes (Kokoro ONNX pipeline)
- ✅ Voice loads (`load_voice()` resolves names)
- ✅ Speech generated (real Kokoro synthesis)
- ✅ WAV saved (UUID-named in `temp/`)
- ✅ SpeechResult returned (immutable frozen dataclass)
- ✅ Tests pass (19/19, 213 total project-wide)
- ✅ Benchmarks pass (warm synthesis ~777ms, target <1.5s)
- ✅ Documentation complete (README in `src/cse/backends/kokoro/`)

### Architecture Validation
PRD-008 proves the CSE architecture is genuinely backend-agnostic:
- Only `backends/kokoro/` imports Kokoro-specific libraries
- The rest of CSE remains completely unaware Kokoro exists
- Deleting `backends/kokoro/` and adding `backends/claire/` would require zero changes to the core

## 2026-07-07 — PRD-009 Implementation (Public Speech Engine API)

### Phase 1: Foundation
- Evaluated AI Skills: `ponytail` enforces a minimal facade pattern. No extra logic, just strict delegation.
- Created `src/cse/api/` with `engine.py`, `config.py`, `lifecycle.py`, and `exceptions.py`.

### Phase 2: Core Components
- `SpeechEngine` class implemented to handle initialization, configuration loading, voice loading, and speech generation pipeline.
- `EngineConfig` implemented to standardize overrides.
- Refactored `src/cse/__init__.py` to export **only** the `SpeechEngine` class, strictly encapsulating all other modules as internal details per PRD-009 §17.

### Phase 3: Tests & Benchmarks
- 14 API unit tests verify initialization, voice loading, speech generation, and lifecycle idempotency.
- Benchmarks show Engine Creation overhead at ~1.6µs (<100ms target) and Speech Request overhead at ~134µs (<10ms target).

### Phase 4: Documentation
- Created `src/cse/api/README.md` with Quick Start examples and lifecycle explanations.

### Verification
- ✅ Engine initializes
- ✅ Voice loads
- ✅ Speech generates
- ✅ SpeechResult returned
- ✅ Shutdown works
- ✅ Tests pass (14/14)
- ✅ Benchmarks pass
- ✅ Documentation complete
