# Kokoro Backend (PRD-008)

The first concrete `AcousticBackend` implementation for the Claire Speech Engine.

Uses [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx) for speech synthesis via ONNX Runtime — no PyTorch dependency at inference time.

---

## Installation

### 1. Install the Python package

```bash
pip install kokoro-onnx soundfile
```

### 2. Download model files

From [kokoro-onnx releases](https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0):

| File | Description |
|------|-------------|
| `kokoro-v1.0.onnx` | ONNX model (~325 MB) |
| `voices-v1.0.bin` | Voice embeddings (~28 MB) |

Place both files in `models/kokoro/` at the project root.

---

## Required Dependencies

| Package | Purpose |
|---------|---------|
| `kokoro-onnx` | Kokoro TTS via ONNX Runtime |
| `soundfile` | WAV file writing |
| `numpy` | Audio array manipulation |
| `onnxruntime` | Inference engine (installed by kokoro-onnx) |

---

## Backend Lifecycle

```
KokoroBackend()
    │
    ▼
initialize()        ← Loads ONNX model + voice embeddings
    │
    ▼
load_voice("af_heart")  ← Selects a Kokoro voice
    │
    ▼
synthesize(timeline) ← Converts timeline → text → audio → WAV
    │
    ▼
SpeechResult         ← Immutable result with audio_path, duration, etc.
    │
    ▼
shutdown()           ← Releases all resources
```

### Thread Safety

Each `KokoroBackend` instance owns its own state. No global Kokoro instance exists. Multiple backends can run concurrently without interference.

---

## Configuration

```python
from cse.backends.kokoro import KokoroConfig

config = KokoroConfig(
    lang_code="en-us",          # Language code
    sample_rate=24000,          # Kokoro native sample rate
    default_voice="af_heart",   # Default voice if none specified
    output_dir="temp",          # WAV output directory
    model_path=Path("models/kokoro/kokoro-v1.0.onnx"),
    voices_path=Path("models/kokoro/voices-v1.0.bin"),
)
```

All fields have sensible defaults. The config is immutable (frozen dataclass).

---

## Usage

```python
from cse.backends.kokoro import KokoroBackend, KokoroConfig

backend = KokoroBackend()
backend.initialize()
backend.load_voice("af_heart")

result = backend.synthesize(timeline)
# result.success == True
# result.audio_path == Path("temp/<uuid>.wav")
# result.duration_seconds > 0

backend.shutdown()
```

---

## Timeline Conversion

The Kokoro backend converts a `PerformanceTimeline` to plain text by extracting only `TOKEN` events. Per PRD-008 §9, expressive features are deliberately ignored:

- ~~Emphasis~~ → Ignored
- ~~Pauses~~ → Ignored
- ~~Breathing~~ → Ignored

Only spoken text is synthesized. Expressive features will be supported by future native Claire models.

---

## Audio Output

- Format: WAV (16-bit PCM via soundfile)
- Sample rate: 24000 Hz (Kokoro native)
- Channels: Mono
- Filename: `<uuid>.wav` (unique, no overwrites)
- Location: `temp/` directory (auto-created)

---

## Error Handling

| Exception | When |
|-----------|------|
| `KokoroInitializationError` | Model files missing, kokoro-onnx not installed, ONNX load failure |
| `VoiceLoadError` | Empty/invalid voice name |
| `SpeechGenerationError` | Backend not initialized, empty text, Kokoro failure, WAV write failure |

All inherit from `KokoroBackendError`.

---

## Known Limitations

1. **No streaming** — Batch synthesis only (single WAV file per call).
2. **No expressive features** — Emphasis, pauses, and breathing from the timeline are ignored.
3. **English only** — Only `en-us` is supported in this version.
4. **CPU only** — Uses `CPUExecutionProvider` by default (GPU can be enabled via `ONNX_PROVIDER` env var).
5. **No voice cloning** — Only pre-trained Kokoro voices are supported.
