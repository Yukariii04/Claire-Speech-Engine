# KittenTTS Backend

The **KittenTTS Backend** is the lightweight, ONNX-powered acoustic synthesis backend for the Claire Speech Engine (CSE).

## Overview

- **Engine:** KittenTTS (v0.8.1, ONNX Runtime)
- **Default Model:** `KittenML/kitten-tts-nano-0.8` (or user-configured 0.8 model)
- **Sample Rate:** 24,000 Hz (24 kHz)
- **Channels:** 1 (Mono)
- **Requires GPU:** No (CPU-optimized)
- **PyTorch Required:** No (Zero PyTorch dependencies at runtime)

## Supported Models

| Model ID | HuggingFace Repo | Size | Parameters | Default |
|---|---|---|---|---|
| `kitten-tts-nano-0.8` | `KittenML/kitten-tts-nano-0.8` | ~25 MB | 15M | Yes |
| `kitten-tts-micro-0.8` | `KittenML/kitten-tts-micro-0.8` | ~45 MB | 40M | No |
| `kitten-tts-mini-0.8` | `KittenML/kitten-tts-mini-0.8` | ~80 MB | 80M | No |

## Supported Voices

| Voice Name (Alias) | Internal Voice ID | Language | Gender |
|---|---|---|---|
| `Bella` | `expr-voice-2-f` | English (US) | Female |
| `Jasper` | `expr-voice-2-m` | English (US) | Male |
| `Luna` | `expr-voice-3-f` | English (US) | Female |
| `Bruno` | `expr-voice-3-m` | English (US) | Male |
| `Rosie` | `expr-voice-4-f` | English (US) | Female |
| `Hugo` | `expr-voice-4-m` | English (US) | Male |
| `Kiki` | `expr-voice-5-f` | English (US) | Female |
| `Leo` | `expr-voice-5-m` | English (US) | Male |

## Installation & Setup

Install KittenTTS models and dependencies via the CSE CLI:

```bash
cse setup
```

## Usage via Python API

```python
from cse import SpeechEngine

engine = SpeechEngine()
engine.load_backend("kittentts")
engine.load_voice("Bella")

result = engine.speak("Welcome to the Claire Speech Engine powered by KittenTTS.")
if result.success:
    print(f"Generated speech: {result.audio_path}")
engine.shutdown()
```

