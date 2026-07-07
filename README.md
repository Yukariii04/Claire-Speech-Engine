# The Claire Speech Engine (CSE)

**The Claire Speech Engine** is a production-grade, backend-agnostic speech synthesis library built in Python. 

## Installation (development)

*(Note: CSE is currently in active development and not yet available on PyPI.)*

To install from source:

```bash
git clone <repo-url> ClaireSpeechEngine
cd ClaireSpeechEngine
pip install -e ".[dev]"
```

## Quick Start

The quickest way to see CSE in action is using the CLI or the Python API.

### CLI

```bash
# List available voices
cse voices

# Generate speech
cse speak --voice claire --text "Hello from The Claire Speech Engine."
```

### Python API

```python
from cse import SpeechEngine

engine = SpeechEngine()
engine.load_voice("claire")

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

## Roadmap

```text
PRD-010 ✅ CLI & Examples
PRD-011 🚧 Packaging & PyPI
PRD-012 🚧 Performance
PRD-013 🚧 Public Beta Readiness
```

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
