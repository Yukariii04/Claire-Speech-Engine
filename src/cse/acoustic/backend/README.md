# Acoustic Backend

## Purpose

The **Acoustic Backend** package establishes the interface boundary between the internal orchestration layer of the Claire Speech Engine and the eventual synthesis models. By creating a strict interface (`AcousticBackend`), the rest of the CSE infrastructure remains entirely decoupled from underlying dependencies (such as Torch, ONNX, Kokoro, etc.).

This package acts as the definitive single source of truth for backend registration, ensuring only validated implementations can process the `PerformanceTimeline`.

## Core Components

- **`AcousticBackend`**: Abstract base class requiring `initialize()`, `shutdown()`, `synthesize()`, and `get_capabilities()`.
- **`BackendCapabilities`**: Immutable dataclass defining what features a backend supports (e.g., streaming, batching, voice cloning).
- **`BackendRegistry`**: A thread-safe singleton-like registry where backend implementations are registered by ID.
- **`BackendManager`**: Manages the lifecycle of a selected backend instance, ensuring it is properly initialized and valid before synthesis occurs.
- **`DummyBackend`**: A default backend used to verify orchestration. It satisfies initialization but explicitly raises `NotImplementedError` upon synthesis.

## Public API

```python
from cse.acoustic.backend import BackendRegistry, BackendManager, DummyBackend

registry = BackendRegistry()
registry.register_backend("dummy", DummyBackend())

manager = BackendManager(registry)
manager.select("dummy")
manager.initialize()

try:
    manager.backend.synthesize(timeline)
except NotImplementedError:
    print("Dummy correctly reached.")
```

## Future Extension

In later iterations (e.g. PRD-006 and beyond), actual synthesis layers will implement the `AcousticBackend` interface. The `VoiceRuntime` will inject these real implementations via the `BackendRegistry`, allowing true audio generation without altering any core orchestration code.
