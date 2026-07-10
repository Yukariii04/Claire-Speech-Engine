# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- Separated Claire Performance Engine (CPE) and Claire Speech Model (CSM) into future distinct workstreams.

### Fixed
- Pre-installed dependency conflicts in Colab (NLTK punkt dataset split, PyTorch 2.6+ `weights_only` defaults).

## [0.11.0-alpha] - 2026-07-07
- Initial private alpha packaging and registry verification.
