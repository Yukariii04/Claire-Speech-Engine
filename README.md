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

### 1. Setup Your Backend
Because CSE is backend-agnostic, the core framework does not ship with heavy ML dependencies. You choose the backend you want and install its specific requirements. 

Currently, CSE officially supports the following backends on **Python 3.12+**:
* **Kokoro**
* **StyleTTS2**

Use the built-in setup tools to automatically download models and install all required ML dependencies for your chosen backend:
```bash
# Install dependencies and download models for Kokoro
cse setup kokoro

# Install dependencies and download models for StyleTTS2
cse setup styletts2
```

### 2. Examples
You can instantly scaffold a runnable example into your current directory to test your setup:
```bash
cse example kokoro
python example_kokoro.py
```

### 3. Check Backend Health
You can view a real-time dashboard of your installed backends, their status, and their voice counts:
```bash
cse backends
```

### 4. Interactive CLI
```bash
# List available voices across all backends
cse voices

# Interactively select your default backend and voice
cse voice
```

### 5. Python API

```python
from cse import SpeechEngine

engine = SpeechEngine()
# Loads your saved CLI preference, or falls back to backend default
engine.load_voice()

speech = engine.speak("Synthesis is now extremely simple.")
if speech.success:
    print(f"Audio saved to: {speech.audio_path}")
```

## Architecture & Vision

Read these documents to understand the core philosophy and design of the engine:
- [Project Vision Document (PVD-001)](docs/PVDs/PVD-001.md)
- [Architecture Overview](docs/Architecture/ARCHITECTURE.md)

## Roadmap

The Claire Speech Engine (CSE) is currently at **v1.0.4**. The core framework is now **feature-frozen** to ensure a stable foundation. 

Future development will transition to:
1. **CPE (Claire Performance Engine)**: Prosody, emotion, and dialogue planning.
2. **CSM (Claire Speech Model)**: Core acoustic ML model training.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Development

### Running Tests
```bash
pytest tests/
```

### Running Benchmarks
```bash
pytest tests/golden/test_perf_golden.py
```
*See [docs/Benchmarks/README.md](docs/Benchmarks/README.md) for full performance targets and reports.*
