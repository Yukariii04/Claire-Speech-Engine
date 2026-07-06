# The Claire Speech Engine API

```python
from cse import SpeechEngine

engine = SpeechEngine()
engine.load_voice("claire")
speech = engine.speak(
    "Hello from The Claire Speech Engine."
)
print(speech.audio_path)
```

## Overview

The Claire Speech Engine (CSE) provides a simple, robust public API for speech synthesis. The entire complexity of the underlying compilation, runtime, and acoustic backend is hidden behind the `SpeechEngine` class.

## Installation

(Not applicable until packaging is implemented. Currently, CSE is used from source).

Ensure you have the necessary dependencies installed via `pip install -e .`

## Quick Start

1. Initialize the engine.
2. Load a voice.
3. Call `speak()`.

```python
from cse import SpeechEngine

engine = SpeechEngine()
engine.load_voice("claire")
result = engine.speak("Welcome to the public API.")

if result.success:
    print(f"Audio saved to: {result.audio_path}")
```

## Configuration

You can configure the engine during initialization using a dictionary, a file path, or an `EngineConfig` object.

```python
from cse import SpeechEngine
from cse.api.config import EngineConfig

# With dictionary overrides
engine = SpeechEngine({"runtime": {"debug": True}})

# With a config path
engine = SpeechEngine("path/to/config.yaml")

# With EngineConfig
engine = SpeechEngine(EngineConfig(overrides={"engine": {"name": "CSE"}}))
```

## Voice Loading

Voices are loaded by their unique string ID. Loading a voice prepares the runtime and acoustic backend.

```python
# List available voices
available_voices = engine.list_voices()
print(available_voices)

# Load a voice
engine.load_voice("af_heart")

# Get metadata of the loaded voice
current_voice = engine.get_voice()
print(current_voice.metadata.name)
```

## Speech Generation

Calling `speak()` executes the entire generation pipeline: Text -> CIR -> Performance Timeline -> Backend Synthesis -> WAV File.

```python
result = engine.speak("Synthesis is now extremely simple.")
```

If speech generation fails, a `SpeechEngineError` is raised.

## Lifecycle

The engine's lifecycle should be safely managed. When finished, call `shutdown()` to release resources. Calling `shutdown()` multiple times is safe (idempotent).

```python
engine = SpeechEngine()
engine.load_voice("claire")
engine.speak("Goodbye.")
engine.shutdown()
```

## Error Handling

The API exposes three typed exceptions:

- `SpeechEngineError`: Base exception for any generic API failure.
- `VoiceNotLoadedError`: Raised if you attempt to call `speak()` without loading a voice first.
- `ConfigurationError`: Raised if you pass an invalid configuration during initialization.
