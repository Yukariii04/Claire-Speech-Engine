# Voice Runtime

## Purpose

The **Voice Runtime** acts as the central orchestrator for the speech pipeline. It does **not** synthesize audio or load ML models itself. Instead, it provides a stable boundary that:
1. Receives a structured `PerformanceTimeline` from the compiler.
2. Manages the currently loaded Voice Package (metadata).
3. Routes the timeline to the active `AcousticBackend`.
4. Manages strict state transitions to prevent pipeline errors.

## Runtime State Machine

The `VoiceRuntime` enforces the following states (`RuntimeState`):
- `UNINITIALIZED`: The runtime is instantiated but hasn't initialized the backend.
- `READY`: Backend initialized, awaiting a voice to be loaded.
- `VOICE_LOADED`: A voice is active and the runtime is ready to process timelines.
- `PROCESSING`: The runtime is currently passing a timeline to the backend for synthesis.
- `SHUTDOWN`: The runtime has safely unloaded voices and shut down the backend.

## Voice Loading (VoiceManager)

The `VoiceManager` currently handles discovery and loading of strictly typed `metadata.yaml` files. It exposes the metadata to the runtime so the backend knows *which* voice to synthesize, without loading heavy models directly into memory at this stage.

## Backend Interface

The `AcousticBackend` is an abstract interface that future audio generators must implement. 

**Dummy Backend**
A default `DummyBackend` is used by the `VoiceRuntime` when no explicit backend is injected. It satisfies the initialization requirements but immediately raises `NotImplementedError` if `synthesize()` is called. This proves that orchestration correctly reached the synthesis phase.

## Public API

```python
from cse.runtime.voice import VoiceRuntime

# 1. Instantiate
runtime = VoiceRuntime()

# 2. Initialize Backend
runtime.initialize()

# 3. Load a Voice Package (metadata)
runtime.load_voice("claire")

# 4. Synthesize (Dummy Backend raises NotImplementedError)
try:
    audio = runtime.process(timeline)
except NotImplementedError:
    print("Orchestration successful!")

# 5. Clean up
runtime.shutdown()
```

## Limitations

- **Synthesis**: Real audio generation is out-of-scope for v1.0.0. The actual synthesis implementation will be introduced in subsequent backend PRDs.
- **Single Voice**: The runtime currently supports loading only one voice at a time. Multi-voice concurrency is not supported.
- **Streaming**: Streaming responses are not supported. The backend expects a complete timeline and returns complete audio.
