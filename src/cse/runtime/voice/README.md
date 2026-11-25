# Voice Runtime

## Purpose

The **Voice Runtime** acts as the central orchestrator for the speech pipeline. It does **not** synthesize audio or load ML models itself. Instead, it provides a stable boundary that:
1. Receives a structured `PerformanceGraph` from the CPE reasoning pipeline.
2. Manages the currently loaded voice ID and runtime configuration.
3. Routes the `PerformanceGraph` to the acoustic synthesis layer (`kittentts` as the primary compatible backend, or experimental native `cam` when weights are available).
4. Manages strict state transitions to prevent pipeline errors.

## Runtime State Machine

The `VoiceRuntime` enforces the following states (`RuntimeState`):
- `UNINITIALIZED`: The runtime is instantiated but hasn't initialized the backend.
- `READY`: Backend initialized, awaiting a voice to be loaded.
- `VOICE_LOADED`: A voice is active and the runtime is ready to process performance graphs.
- `PROCESSING`: The runtime is currently passing a graph to the backend for synthesis.
- `SHUTDOWN`: The runtime has safely unloaded voices and shut down the backend.

## Voice Loading

Voice loading first validates the voice ID directly against the active backend when that backend enumerates voices (such as `kittentts` supporting `Bella`, `Bruno`, `expr-voice-2-f`, or `cam` supporting `cam-speaker_0-default`, etc.) and stores a `BackendVoiceInfo` object (sharing `.metadata` without claiming a filesystem `VoicePackage` path; `metadata.license` is `None` when the backend does not provide licensing info). For backends that do not enumerate voices (such as `dummy`), it resolves a registered `VoicePackage` from the package registry.

## Backend Interface & Plumbing

The `AcousticBackend` is the translation interface (implementing `BaseTranslator`) through which acoustic engines consume the `PerformanceGraph`.

**Dummy Backend**
A default `DummyBackend` is used by the `VoiceRuntime` when no explicit backend is injected. It satisfies initialization requirements but immediately raises `NotImplementedError` if `translate()` is called, verifying that orchestration reached the synthesis stage.

## Public API

```python
from cse.runtime.voice import VoiceRuntime
from cse.performance.graph import PerformanceGraph

# 1. Instantiate
runtime = VoiceRuntime()

# 2. Initialize runtime and load KittenTTS compatible backend
runtime.initialize()
runtime.load_backend("kittentts")

# 3. Load a Voice
runtime.load_voice("Bella")

# 4. Process Performance Graph
graph = PerformanceGraph(
    text="Hello world.",
    character_state=None,
    semantics={},
    intent={},
    plan={},
)
result = runtime.process(graph)

# 5. Clean up
runtime.shutdown()
```

## Features & Constraints

- **Runtime Plumbing**: `runtime.load_backend(id)` switches the synthesis backend (`"kittentts"`, experimental `"cam"`, or `"dummy"`).
- **Single Active Voice**: The runtime manages one active voice at a time for synthesis dispatch.
- **State Validation**: Strict state guards prevent processing before initialization and voice loading.
