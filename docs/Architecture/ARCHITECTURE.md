# Claire Speech Engine Architecture

This document provides a high-level overview of the Claire Speech Engine (CSE) architecture. CSE is designed to be highly modular, separating the orchestration of speech from the actual acoustic generation.

## `SpeechEngine`

The `SpeechEngine` is the primary public entry point for applications integrating CSE. It provides a clean, stable API facade over the internal complexity of the framework. Developers interact almost exclusively with this class to load voices, switch backends, and synthesize text.

## `Runtime`

The `Runtime` manages the lifecycle and internal state of the engine. It enforces strict state transitions (e.g., `UNINITIALIZED` -> `READY`) to guarantee thread safety and predictable behavior. When `SpeechEngine.speak()` is called, the `Runtime` is responsible for compiling the input text into a `PerformanceTimeline` and routing it to the active backend.

## `Backend Interface`

The `AcousticBackend` is an abstract interface that defines how the engine interacts with speech models. Every backend (whether local, API-based, or mocked) must implement this interface. It requires defining:
- Initialization and shutdown logic.
- Voice loading.
- The `synthesize()` method, which accepts a `PerformanceTimeline` and yields audio data.
- The reporting of `BackendCapabilities` (e.g., sample rate, streaming support).

## `Backend Registry`

The `BackendRegistry` is a thread-safe singleton responsible for discovering and maintaining available backends. It parses backend packages to determine their capabilities and registers them dynamically. The `SpeechEngine` queries this registry when a developer requests a backend switch.

## `SpeechResult`

A `SpeechResult` is the immutable output object returned to the user upon successful (or failed) synthesis. It encapsulates:
- The generated audio data or the path to the saved audio file.
- Success status and error messages.
- Performance metrics (e.g., time-to-first-byte, total generation time).

## Evaluation Backends

CSE includes evaluation backends (such as the `dummy` backend) designed for CI/CD and testing. These backends conform strictly to the `AcousticBackend` interface but do not invoke real machine learning models. They allow developers to test the entire lifecycle, configuration, and state transitions of the framework instantly and without requiring GPU hardware.
