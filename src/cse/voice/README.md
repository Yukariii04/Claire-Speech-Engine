# Voice Package System

## Purpose

The **Voice Package System** allows the Claire Speech Engine to treat voices as independent, installable packages rather than loose model files or hardcoded configurations. By standardizing the concept of a voice package, the engine remains entirely decoupled from any specific acoustic or vocoder technology.

The runtime simply says: "Load voice `claire`", and the package system locates the metadata, validates its integrity, registers it in memory, and prepares it for the active backend.

## Directory Structure

A complete voice package looks like this:

```text
voices/
    claire/
        metadata.yaml      # (Required) Versioning, capabilities, backend info
        pronunciation/     # (Future) Custom dictionaries
        acoustic/          # (Future) Model weights
        vocoder/           # (Future) Vocoder weights
        assets/            # (Future) Identity assets, images
        license.txt        # Package license
```

*Note: For the PRD-007 implementation, only `metadata.yaml` is actively parsed.*

## Metadata Format

The `metadata.yaml` file defines the contract between the voice package and the engine.

```yaml
id: claire
name: Claire
version: 1.0.0
author: Claire Speech Engine
language: en
backend: dummy
sample_rate: 24000
channels: 1
description: Default Claire development voice
license: MIT
```

## Public API

```python
from cse.voice import (
    load_voice_package,
    register_voice_package,
    get_voice_package,
    list_voice_packages
)

# 1. Load from disk
pkg = load_voice_package("path/to/voices/claire")

# 2. Register globally
register_voice_package(pkg)

# 3. Retrieve anywhere
active_pkg = get_voice_package("claire")
```

## Future Compatibility

This package structure is designed so that when real models (e.g., ONNX weights) are introduced, they simply become additional files inside the package directory, and the `VoiceMetadata` schema will expand to map them. The core `VoiceRuntime` engine code will not need to change.
