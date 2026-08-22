# The Claire Speech Engine (CSE)

**The Claire Speech Engine** is a production-grade, lightweight speech synthesis library built in Python.

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

### 1. Setup Backend & Pre-download Models
CSE currently uses **KittenTTS** (CPU-optimized, ONNX Runtime) as its compatible acoustic synthesis implementation on **Python 3.10 – 3.12** while native CAM is under development.

```bash
# Setup KittenTTS dependencies and pre-download models for offline use
cse setup
```

### 2. Examples
You can instantly scaffold a runnable example into your current directory to test your setup:
```bash
cse example
python example_kittentts.py
```

### 3. Interactive CLI
```bash
# List available KittenTTS models (Nano, Micro, Mini)
cse models

# Interactively select your default model
cse model

# Interactively select your default voice
cse voice
```

### 4. Python API

```python
from cse import SpeechEngine

engine = SpeechEngine()
engine.load_backend("kittentts")
# Loads your saved CLI preference, or falls back to backend default ('expr-voice-2-f' / 'Bella')
engine.load_voice()

speech = engine.speak("Synthesis is now extremely simple and lightweight.")
if speech.success:
    print(f"Audio saved to: {speech.audio_path}")
```

## Architecture & Vision

Read these documents to understand the core philosophy and design of the engine:
- [Project Vision Document (PVD-001)](docs/PVDs/PVD-001.md)
- [Architecture Overview](docs/Architecture/ARCHITECTURE.md)

## System Overview & Roadmap

The Claire Speech Engine (CSE) is currently at **v1.0.5**:
1. **CSE (Complete Engine & Orchestration)**: Runtime lifecycle, streaming transport, voice registries, CLI tools, and packaging.
2. **CPE (Claire Performance Engine)**: Communication and performance reasoning passes (`meaning` -> `intent` -> `planning`) producing the canonical `PerformanceGraph`.
3. **Acoustic Synthesis**: Currently utilizing KittenTTS (compatible ONNX implementation) while native CAM is under development.

### Intended Project Architecture:
- **CSE**: Complete speech engine coordinating reasoning and acoustic realization.
- **CPE**: Rich communication reasoning, intent enrichment, and delivery planning.
- **PerformanceGraph**: Canonical, immutable contract between CPE and CAM.
- **CAM (Claire Acoustic Model)**: Native, in-house acoustic renderer designed to interpret the `PerformanceGraph` directly.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Development

### Running Tests
```bash
pytest tests/
```

### Running Golden Tests
```bash
pytest tests/golden/test_perf_golden.py
```
*See [docs/Benchmarks/README.md](docs/Benchmarks/README.md) for full performance targets and reports.*
