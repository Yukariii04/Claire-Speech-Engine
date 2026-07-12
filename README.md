# The Claire Speech Engine (CSE)

**The Claire Speech Engine** is a production-grade, backend-agnostic speech synthesis library built in Python. 

## Installation

```bash
pip install claire-speech-engine
```

To install from source for development:

```bash
git clone https://github.com/Yukariii04/Claire-Speech-Engine.git
cd Claire-Speech-Engine
pip install -e ".[dev]"
```

## Quick Start

The quickest way to see CSE in action is using the CLI or the Python API.

### CLI

```bash
# List available voices across all backends
cse voices

# Interactively select your default backend and voice
cse voice

# Generate speech (uses your selected default if --voice is omitted)
cse speak --text "Hello from The Claire Speech Engine."
```

### Python API

```python
from cse import SpeechEngine

engine = SpeechEngine()
# Loads your saved CLI preference, or falls back to backend default
engine.load_voice()

speech = engine.speak("Synthesis is now extremely simple.")
if speech.success:
    print(f"Audio saved to: {speech.audio_path}")
```

## Examples

We believe every feature should be easily discoverable. Check the `examples/` directory for runnable scripts:

- `examples/basic.py` — Simple end-to-end synthesis.
- `examples/configuration.py` — How to pass custom overrides and load configurations.
- `examples/list_voices.py` — Querying the local voice registry.
- `examples/generate_speech.py` — Handling output files and moving them dynamically.

## Architecture & Vision

Read these documents to understand the core philosophy and design of the engine:
- [Project Vision Document (PVD-001)](docs/PVDs/PVD-001.md)
- [Architecture Overview](docs/Architecture/ARCHITECTURE.md)

## Roadmap

The Claire Speech Engine (CSE) has officially reached **v1.0.0-beta**. The core framework is now **feature-frozen** to ensure a stable foundation. 

Future development will transition to:
1. **CPE (Claire Performance Engine)**: Prosody, emotion, and dialogue planning.
2. **CSM (Claire Speech Model)**: Core acoustic ML model training.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Development

### Running Tests
```bash
pytest
```

### Running Benchmarks
```bash
pytest benchmarks/ --benchmark-only
```
*See [docs/Benchmarks/README.md](docs/Benchmarks/README.md) for full performance targets and reports.*
