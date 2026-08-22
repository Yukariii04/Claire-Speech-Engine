# Acoustic Backend

## Purpose

The **Acoustic Backend** package establishes the contract boundary for acoustic realization within the Claire Speech Engine (CSE).

In the CSE architecture:
1. **CPE** produces the canonical, immutable `PerformanceGraph`.
2. **CAM** is the native acoustic model designed to consume the `PerformanceGraph` directly to synthesize speech.
3. **Compatible Acoustic Implementations** (such as KittenTTS) implement the `AcousticBackend` interface (subclassing `BaseTranslator`) to translate and satisfy the `PerformanceGraph` contract.

This package provides the single source of truth for backend registration and lifecycle management, ensuring only validated implementations process the `PerformanceGraph`.

## Core Components

- **`AcousticBackend`**: Abstract base class (subclass of `BaseTranslator`) requiring `initialize()`, `shutdown()`, `translate()`, `get_capabilities()`, and `validate_graph()`.
- **`BackendCapabilities`**: Immutable dataclass defining what features a backend supports (e.g., `backend_name`, `sample_rate`, `emotion`, `supports_streaming`, `supported_languages`).
- **`BackendRegistry`**: A thread-safe registry where backend implementations are registered by ID.
- **`BackendManager`**: Manages the lifecycle of a selected backend instance, ensuring it is properly initialized and valid before synthesis occurs.
- **`DummyBackend`**: A default backend used to verify orchestration. It satisfies initialization but explicitly raises `NotImplementedError` upon `translate()`.

## Public API

```python
from cse.acoustic.backend import BackendRegistry, BackendManager, DummyBackend
from cse.performance.graph import PerformanceGraph

registry = BackendRegistry()
registry.register_backend("dummy", DummyBackend())

manager = BackendManager(registry)
manager.select("dummy")
manager.initialize()

try:
    manager.backend.translate(graph)
except NotImplementedError:
    print("Dummy correctly reached.")
```

## Implementation Contract

Acoustic synthesis layers (such as `KittenTTSBackend` in `src/cse/backends/kittentts/`) implement the `AcousticBackend` interface to translate `PerformanceGraph` instances into audio waveforms. The `VoiceRuntime` routes the `PerformanceGraph` through the loaded acoustic implementation to complete speech synthesis.
