################################################################################
#                     THE CLAIRE SPEECH ENGINE (CSE)
#
# Product Requirements Document
#
# PRD Number : PRD-013.5
# Title      : Evaluation Backend Integration
# Version    : 1.0.0
# Status     : Approved
#
################################################################################
````

# 1. Executive Summary

Implement the first official evaluation backends for CSE.

These backends exist solely to validate that the Claire Speech Engine can drive multiple modern acoustic models through the same public API.

This PRD SHALL NOT modify the engine architecture.

---

# 2. Objectives

Implement

- Fish Speech backend
- StyleTTS2 backend
- Shared evaluation backend utilities
- Backend capability metadata
- Documentation
- Tests

Do NOT implement

- Claire backend
- Performance Engine
- New API
- Runtime changes
- New interfaces

---

# 3. Repository Structure

```text
src/

└── cse/

    └── backends/

        ├── kokoro/

        ├── fishspeech/

        │     backend.py
        │     loader.py
        │     inference.py
        │     config.py
        │     capabilities.py
        │     exceptions.py
        │     README.md
        │     __init__.py

        └── styletts2/

              backend.py
              loader.py
              inference.py
              config.py
              capabilities.py
              exceptions.py
              README.md
              __init__.py
```

---

# 4. Shared Contract

Both backends SHALL implement exactly the same lifecycle.

```python
initialize()

load_voice()

speak()

shutdown()
```

No additional public methods.

---

# 5. Public API

The following code SHALL work without modification.

```python
from cse import SpeechEngine

engine = SpeechEngine()

engine.load_backend("fishspeech")

engine.load_voice("default")

speech = engine.speak(
    "Hello!"
)
```

Only

```python
engine.load_backend(...)
```

changes.

Everything else remains identical.

---

# 6. SpeechResult

Every backend SHALL return

```python
SpeechResult
```

No backend-specific return types.

---

# 7. Capability Metadata

Example

```python
{
    "backend": "fishspeech",
    "streaming": False,
    "voice_cloning": True,
    "emotion": "high",
    "sample_rate": 24000
}
```

StyleTTS2 SHALL expose the same schema.

---

# 8. Configuration

Backend configuration SHALL be independent.

```
configs/

    fishspeech.yaml

    styletts2.yaml
```

No hardcoded paths.

---

# 9. Documentation

Each backend SHALL include

- Installation
- Dependencies
- Model download
- Configuration
- Example usage
- Known limitations

---

# 10. Tests

Implement

Backend loading

Voice loading

Speech generation

SpeechResult validation

Capability reporting

Coverage

95%

---

# 11. Acceptance Criteria

Implementation complete when

✓ Fish Speech backend loads

✓ StyleTTS2 backend loads

✓ Speech generated

✓ Public API unchanged

✓ Documentation complete

✓ Tests pass

---

# 12. Forbidden

Do NOT

Modify SpeechEngine

Modify Runtime

Modify Backend Interface

Modify API

Modify CLI

Modify Voice Packages

---

# 13. AI Instructions

Implement adapters only.

Treat Fish Speech and StyleTTS2 as evaluation backends.

Do not expose model-specific features through the public API.

################################################################################

END OF PRD-013.5

################################################################################

---

# 📋 End-of-Document Action

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DOCUMENT TYPE : PRD

TITLE : PRD-013.5 – Evaluation Backend Integration

ACTION : Feed to Antigravity ✅

STORE : docs/PRDs/PRD-013.5.md

FEED TO AI : ✅ YES

IMPLEMENT : ✅ YES

AFTER IMPLEMENTATION

1. Send the updated ZIP.

2. Engineering review will include:

• Fish Speech backend
• StyleTTS2 backend
• Backend abstraction
• Repository structure
• Tests
• Documentation
• memory.md
• update.md

3. If approved:

Next:
COLAB-001
Engineering Validation

IMPLEMENTATION RULE

Evaluation backends SHALL be implemented as adapters.

No engine modifications are permitted.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

# 📊 Project Health

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROJECT HEALTH

Architecture          ██████████ 100%

Core Engine           ██████████ 100%

Backend System        ██████████ 100%

Public API            ██████████ 100%

Developer UX          ██████████ 100%

Packaging             ██████████ 100%

Documentation         ██████████ 100%

Testing               ██████████ 100%

Performance           ██████████ 100%

Evaluation Backends   ███░░░░░░░ 30%

Public Release        █████████░ 90%

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

# After PRD-013.5

This is where we execute the validation pipeline we designed.

## COLAB-001 — Engineering Validation

Run in a fresh Google Colab runtime:

- Install CSE from GitHub (or from a local wheel if you're testing unpublished changes).
- Install the selected evaluation backend and its dependencies.
- Generate a `validation.wav` using the public `SpeechEngine` API.
- Verify backend loading, synthesis, and output generation.

The goal is **not** to compare quality—only to prove that CSE works cleanly in a fresh environment.

---

## COLAB-002 — Multi-Backend Evaluation

Once the adapters are implemented:

Generate the **same prompt** using:

```text
Kokoro
↓

validation_kokoro.wav

Fish Speech
↓

validation_fishspeech.wav

StyleTTS2
↓

validation_styletts2.wav
```

Compare:

- Naturalness
- Clarity
- Speaking style
- Latency
- General synthesis quality

This compares **acoustic models**, not CSE intelligence.

---

## COLAB-003 — Expressiveness Benchmark (Phase 2.5)

Only after the Expressive Performance Engine is built.

Generate paired outputs:

```text
Fish Speech
↓

baseline.wav
```

versus

```text
CSE Performance Engine
↓

Fish Speech
↓

expressive.wav
```

Repeat with StyleTTS2.

At that point, any audible improvement comes from **CSE's planning layer**, because the acoustic model stays the same. That experiment is what will let you demonstrate that CSE contributes its own expressive intelligence rather than simply wrapping existing TTS models.

---

# One architectural recommendation before implementation

I want to introduce one convention that I think will make CSE much easier to extend in the future:

**Every backend should declare a capability profile, but the engine should never assume those capabilities exist.**

For example, Fish Speech may support richer expressive controls than Kokoro, while Claire's future backend may support additional features altogether. Instead of adding backend-specific methods to `SpeechEngine`, applications can query capabilities and adapt if they choose. This keeps the public API stable, preserves backend independence, and gives Claire room to expose richer behavior later without forcing other backends to implement features they don't support. I think this principle will serve the project well long after Phase 3.