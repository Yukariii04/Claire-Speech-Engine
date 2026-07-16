# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Documented `numpy` version conflicts between Kokoro and StyleTTS2 backends.
- Added notes regarding the future transition to the Claire Acoustic Model (CAM) and the temporary nature of third-party backends.

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
