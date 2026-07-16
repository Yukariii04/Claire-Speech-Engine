# Backend Architecture & Validation

The Claire Speech Engine (CSE) is designed to be **backend-agnostic**. The core engine orchestrates text processing, intermediate representation (CIR), and performance compilation, but the final audio synthesis is delegated to an `AcousticBackend`.

This ensures that the engine can drive any compatible TTS model without requiring architectural changes.

## Supported Backends

| Backend | Status | Notes |
|---------|--------|-------|
| `dummy` | Active | Used for testing and validation without GPU. |
| `kokoro` | Active | Development backend. Requires `kokoro-onnx`. |
| `styletts2` | Active | Fast evaluation backend. |

> [!WARNING]
> **Numpy Conflict:** Running setup for both `kokoro` and `styletts2` consecutively and then trying to switch between them will not work due to a `numpy` version conflict. You must run the setup for the backend you intend to use right before using it.

> [!NOTE]
> **Future Development:** Third-party backends (like `kokoro` and `styletts2`) are currently supported because CSE's own acoustic model (Claire Acoustic Model) is under development. Since these external backends differ in design, they cannot fully adopt the Claire Performance Engine. After the Claire acoustic model is released, support for these backends will continue as long as they don't conflict with CSE's core architecture.

## Backend Switching

Switching backends is done seamlessly via the public API:

```python
from cse import SpeechEngine

engine = SpeechEngine()
engine.load_backend("kokoro")  # Switches the active backend
engine.load_voice("af_heart")
speech = engine.speak("Hello world.")
```

## Capability Reporting

Applications can query a backend's capabilities at runtime to adapt their workflows:

```python
caps = engine.get_backend_capabilities()
print(caps["streaming"])      # True/False
print(caps["emotion"])        # "limited", "full", "none"
print(caps["sample_rate"])    # e.g., 24000
```

## Implementing a New Backend

To implement a new backend:
1. Inherit from `cse.acoustic.backend.interface.AcousticBackend`.
2. Implement `initialize()`, `shutdown()`, `synthesize()`, `get_capabilities()`, and `validate_timeline()`.
3. Ensure you return `BackendCapabilities` detailing the backend's limitations.
4. Register the backend in `engine.load_backend()` or the `BackendRegistry`.

## Evaluation Methodology

Use the included evaluation scripts to compare output across backends:

```bash
python evaluation/compare.py
```

This runs a standard set of prompts (`evaluation/prompts/standard.txt`) across all registered backends and places the generated audio in `evaluation/outputs/<backend>/`.
