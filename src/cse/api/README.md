# The Claire Speech Engine API

```python
from cse import SpeechEngine

engine = SpeechEngine()
engine.load_voice("Bella")
speech = engine.speak(
    "Hello from The Claire Speech Engine."
)
print(speech.audio_path)
```

## Overview

The Claire Speech Engine (CSE) provides a simple, robust public API for speech synthesis. The entire complexity of the underlying compilation, runtime, and acoustic backend is hidden behind the `SpeechEngine` class.

## Installation

```bash
pip install claire-speech-engine
```

Or install from source for local development:

```bash
git clone https://github.com/Yukariii04/Claire-Speech-Engine.git
cd Claire-Speech-Engine
pip install -e ".[dev]"
```

## Quick Start

1. Initialize the engine.
2. Load a voice (or call `engine.load_voice()` to use your saved preference).
3. Call `speak()`.

```python
from cse import SpeechEngine

engine = SpeechEngine()
engine.load_backend("kittentts")
engine.load_voice("Bella")
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

Voices are loaded by their unique name or alias (e.g., `"Bella"`, `"Bruno"`, `"expr-voice-2-f"`). Calling `load_voice()` without arguments automatically resolves your preferred voice from CLI configuration (`cse voice`).

```python
# List available voices
available_voices = engine.list_voices()
print(available_voices)

# Load a voice by alias or ID
engine.load_voice("Bella")

# Get metadata of the loaded voice
current_voice = engine.get_voice()
print(current_voice.metadata.name)
```

## Speech Generation

Calling `speak()` executes the generation pipeline: Text -> PerformanceContext -> ReasoningPipeline -> PerformanceGraph -> Runtime -> Backend Synthesis -> WAV File.

```python
result = engine.speak("Synthesis is now extremely simple.")
```

If speech generation fails, a `SpeechEngineError` is raised.

## Lifecycle

The engine's lifecycle should be safely managed. When finished, call `shutdown()` to release resources. Calling `shutdown()` multiple times is safe (idempotent).

```python
engine = SpeechEngine()
engine.load_backend("kittentts")
engine.load_voice("Bella")
engine.speak("Goodbye.")
engine.shutdown()
```

## Error Handling

The API exposes three typed exceptions:

- `SpeechEngineError`: Base exception for any generic API failure.
- `VoiceNotLoadedError`: Raised if you attempt to call `speak()` without loading a voice first.
- `ConfigurationError`: Raised if you pass an invalid configuration during initialization.
