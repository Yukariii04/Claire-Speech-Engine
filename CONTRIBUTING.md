# Contributing to Claire Speech Engine

First off, thank you for considering contributing to the Claire Speech Engine (CSE)!

## Development Philosophy

CSE is the foundation of the Claire project. Its sole purpose is to provide a fast, stable, backend-agnostic framework for speech synthesis. 
As of `v1.0.0-beta`, the framework itself is feature-frozen for stability. 

**What we accept:**
- Bug fixes
- Performance optimizations
- Documentation improvements
- New officially supported backends (if they meet the `AcousticBackend` interface)

**What we do NOT accept:**
- Core architectural changes to the framework
- New complex logic in `SpeechEngine`
- LLM or AI code embedded directly into the core (these belong in the Performance Engine)

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
4. Check performance regressions (must be < 50ms):
   ```bash
   pytest benchmarks/ --benchmark-only
   ```

## Pull Request Process

1. Ensure any install or build dependencies are removed before the end of the layer when doing a build.
2. Update the README.md with details of changes to the interface, this includes new environment variables, exposed ports, useful file locations and container parameters.
3. You may merge the Pull Request in once you have the sign-off of two other developers, or if you do not have permission to do that, you may request the second reviewer to merge it for you.
