# The Claire Speech Engine (CSE)

**The Claire Speech Engine** is a production-grade, backend-agnostic speech synthesis library built in Python. 

## What is CSE?

CSE is a unified pipeline for generating high-quality speech. It cleanly abstracts away the complexity of parsing text, compiling performance timelines, and routing audio generation through acoustic backends (like Kokoro ONNX). 

You feed it text, and it gives you speech.

## Why use it?

- **Simple Public API:** A single `SpeechEngine` class orchestrates the entire lifecycle.
- **Backend-Agnostic:** Designed from the ground up to support multiple AI acoustic models without changing your code.
- **Immutable & Fast:** Core data structures (CIR, Performance Timelines, Audio Streams) are completely immutable and blazing fast.
- **Developer First:** Built with clean architecture, typed exceptions, and no heavy boilerplate.

## Quick Start

The quickest way to see CSE in action is using the CLI:

```bash
# List available voices
python cse.py voices

# Generate speech
python cse.py speak --voice claire --text "Hello from The Claire Speech Engine."
```

Or from Python:

```python
from cse import SpeechEngine

engine = SpeechEngine()
engine.load_voice("claire")

speech = engine.speak("Synthesis is now extremely simple.")
if speech.success:
    print(f"Audio saved to: {speech.audio_path}")
```

## Installation

*(Note: CSE is currently in active development and not yet available on PyPI.)*

To install from source:

```bash
git clone <repo-url> ClaireSpeechEngine
cd ClaireSpeechEngine
pip install -e ".[dev]"
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
