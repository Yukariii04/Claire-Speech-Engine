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
