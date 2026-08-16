# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.5] - 2026-08-16

### Breaking Changes
- **Acoustic Backend Migration**: Replaced Kokoro and StyleTTS2 acoustic backends with KittenTTS (v0.8.1).
- **Kokoro & StyleTTS2 Excised**: Complete removal of Kokoro and StyleTTS2 backend implementations, tests, models, configuration, voice mappings, and CLI branches.
- **Dependencies Cleaned**: Excised PyTorch (`torch`) and `torchaudio` direct dependencies. Now runs lightweight via ONNX Runtime and `kittentts` with official Python 3.13+ support.
- **CLI Streamlined**:
  - Removed obsolete top-level `cse voices` and `cse backends` commands.
  - Added `cse models` to list supported KittenTTS models with sizes and parameter counts.
  - Added `cse model` (`set`, `current`, `reset`, interactive) for model selection.
  - Simplified `cse voice` to directly select KittenTTS voices without redundant backend prompt.
  - Upgraded `cse setup` to automatically pre-download and cache all supported KittenTTS models (`kitten-tts-nano-0.8`, `kitten-tts-micro-0.8`, `kitten-tts-mini-0.8`) for offline access.

### Added
- **KittenTTS Backend**: Created `src/cse/backends/kittentts/` implementing `AcousticBackend` and `BaseTranslator` with deferred asset loading, real ONNX synthesis, and speed mapping from PerformanceGraph pace.
- **KittenTTS Scaffold & Examples**: Added `example_kittentts.py` scaffold and updated `examples/basic.py`, `examples/generate_speech.py`, and `evaluation/compare.py`.
- **KittenTTS Test & Benchmark Suite**: Added `tests/test_kittentts_backend.py` and `benchmarks/test_kittentts_backend.py` with full unit, mocked, and real end-to-end integration tests.

### Fixed
- **KittenTTS Installation References**: Updated `KittenTTSInitializationError` to direct users to `cse setup`.
- **Automated Setup Single Source of Truth**: Fixed `command_setup()` to install using the pinned KittenTTS 0.8.1 release wheel URL.
- **Benchmark Suite Restored**: Fully restored all 12 benchmark test suites. Removed stray `.benchmarks/.gitkeep` artifact.
- **Prose Documentation Deep Cleaned**: Removed remaining Kokoro/StyleTTS2 references from `ARCHITECTURE.md`, `PVD-001.md`, `lexicon.md`, `constitution.md`, and deleted the `/kokoro/` rule from `.gitignore`.
- **Direct Dependencies Declared**: Explicitly declared `phonemizer` and `huggingface_hub` in `pyproject.toml` and `requirements.txt`.

## [1.0.4] - 2026-07-13

### Fixed
- Resolved version string mismatches across the repository.
- Fixed release validation test failures related to missing sections in `README.md`.

## [1.0.3] - 2026-07-13

### Added
- Full 54-voice set and 9 language support for Kokoro backend.
- Developer toolkit commands: `cse example` (scaffolding) and `cse backends` (health dashboard).
- Interactive voice selection via CLI (`cse voice`) with persistent configuration.

### Changed
- Deferred asset checks to `synthesize()` for all backends to improve initialization time.
- StyleTTS2 threading safety enhancements and `claire_neutral` default voice.

### Removed
- **Fish Speech Backend Removed**: Excised due to severe Python 3.12+ dependency conflicts (PyTorch, Lightning, C++ extensions) that broke environment stability.

## [1.0.2] - 2026-07-12

### Added
- Abstracted `AcousticBackend` voice discovery (`list_voices()`, `validate_voice()`).
- Persistent CLI preferences via `user_config.py`.

### Changed
- `VoiceRuntime` now delegates voice loading fully to the backends.
- Removed `cse.py` root script to resolve import namespace collisions.

## [1.0.0-beta] - 2026-07-10

### Added
- Feature-complete framework architecture (v1 API).
- Dynamic backend registry and switching (`engine.load_backend()`).
- High-performance streaming interface (`cse.streaming.audio`).
- Unified Performance Timeline architecture (`cse.performance.compiler`).
- `cse` Command Line Interface (CLI) for synthesis and voice listing.
- Two production-ready backends: `fishspeech` (v1.5) and `styletts2`.
- End-to-end evaluation pipeline with COLAB-001 reference architecture.
- Full architectural and vision documentation (`ARCHITECTURE.md`, `PVD-001.md`).

### Changed
- Shifted from single-backend implementation to agnostic adapter pattern.
- Separated Claire Performance Engine (CPE) and Claire Acoustic Model (CAM) into future distinct workstreams.

### Fixed
- Pre-installed dependency conflicts in Colab (NLTK punkt dataset split, PyTorch 2.6+ `weights_only` defaults).

## [0.11.0-alpha] - 2026-07-07
- Initial private alpha packaging and registry verification.
