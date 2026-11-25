# Acoustic Backend Architecture & Synthesis Layer

The Claire Speech Engine (CSE) coordinates text processing and communication reasoning via the Claire Performance Engine (CPE) to produce an immutable `PerformanceGraph`. The native and intended acoustic model of CSE is CAM (Claire Acoustic Model), which renders the `PerformanceGraph` into speech waveforms.

```text
CSE
 └── CPE
      └── PerformanceGraph (Contract)
           └── CAM
                └── Speech
```

While KittenTTS serves as the active default compatible acoustic implementation satisfying the CAM contract via translation, native `cam` (`CAMBackend`) is exposed experimentally in `VoiceRuntime` and requires released ONNX weights (`ClaireAI/cam-001-expresso-read`) or local `CAMConfig` model paths (`resolve_cam_model_paths()` raises `FileNotFoundError` when trained weights are absent). A lightweight `dummy` backend is also available for framework testing and pipeline validation.

## Supported Acoustic Implementations

| Backend | Status | Role |
|---|---|---|
| `kittentts` | Active (Default) | Compatible acoustic implementation (v0.8.1 ONNX). Translates `PerformanceGraph` to audio. |
| `cam` | Experimental | Native Claire Acoustic Model (`CAMBackend`, two-stage ONNX Runtime). Requires released/local trained weights. |
| `dummy` | Active | Framework testing backend without audio models. |

## Runtime Backend Invocation

To invoke the current compatible acoustic implementation at runtime:

```python
from cse import SpeechEngine

engine = SpeechEngine()
engine.load_backend("kittentts")  # Loads KittenTTS compatible implementation
engine.load_voice("expr-voice-2-f")
speech = engine.speak("Hello world.")
```

To invoke the experimental native CAM backend (requires ONNX weights in `~/.cache/claire/cam/v1.0.0`, `$CSE_CAM_CACHE_DIR`, or a released checkpoint at `ClaireAI/cam-001-expresso-read`):

```python
from cse import SpeechEngine

engine = SpeechEngine()
engine.load_backend("cam")
engine.load_voice("cam-speaker_0-default")
speech = engine.speak("Hello from native CAM.")
```

## Capability Reporting

Applications can query the loaded synthesis backend's capabilities at runtime to adapt their workflows:

```python
caps = engine.get_backend_capabilities()
print(caps["supports_streaming"])  # True/False
print(caps["emotion"])             # "limited", "full", "none"
print(caps["sample_rate"])         # e.g., 24000
```

## Implementing a Compatible Adapter

To implement an acoustic adapter that satisfies the CAM contract:
1. Inherit from `cse.acoustic.backend.interface.AcousticBackend`.
2. Implement `initialize()`, `shutdown()`, `translate()`, `get_capabilities()`, and `validate_graph()`.
3. Ensure you return `BackendCapabilities` detailing supported features.
4. Register the backend in `engine.load_backend()` or `VoiceRuntime`.

## Evaluation Utilities

Use the evaluation script to verify acoustic synthesis across standard prompts:

```bash
python evaluation/compare.py
```

This runs standard prompts (`evaluation/prompts/standard.txt`) through registered synthesis adapters and places output in `evaluation/outputs/<backend>/`.
