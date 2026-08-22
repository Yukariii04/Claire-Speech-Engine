# Contributing to Claire Speech Engine

First off, thank you for considering contributing to the Claire Speech Engine (CSE)!

## Development Philosophy

CSE is the complete speech engine foundation of the Claire project, coordinating communication reasoning via CPE and acoustic realization via CAM (with KittenTTS as the current compatible implementation).

**What we accept:**
- Bug fixes
- Performance optimizations
- Documentation improvements
- Acoustic backend adapters that satisfy the `PerformanceGraph` translation contract

**What we do NOT accept:**
- Unnecessary runtime dependencies (such as heavy frameworks or unneeded C++ extensions)
- Tightly coupling acoustic backends to core orchestration
- Learned AI models embedded directly into core deterministic reasoning passes

## Development Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/Yukariii04/Claire-Speech-Engine.git
   cd Claire-Speech-Engine
   ```
2. Install with dev dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
3. Run tests before submitting a PR:
   ```bash
   pytest
   ```
4. Check performance regressions (must pass threshold assertions):
   ```bash
   pytest benchmarks/ --benchmark-only
   ```

## Pull Request Process

1. Ensure all test and benchmark suites pass cleanly (`pytest` and `pytest benchmarks/ --benchmark-only`).
2. Adhere to the established code architecture (CSE orchestration vs. CPE performance reasoning vs. acoustic backends).
3. Update relevant documentation and README files if modifying public APIs, CLI subcommands, or backend capabilities.
4. Submit a clear Pull Request describing your changes, motivation, and verification steps.
