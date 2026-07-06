# Performance Compiler

## Purpose

The **Performance Compiler** is responsible for converting the structured language representation (`CIRDocument`) into a deterministic performance plan called a **Performance Timeline**.

It decides **how** speech should be performed, resolving:
- Speech pacing (timing)
- Pauses and hesitations
- Emphasis
- Breathing events
- Expressive performance attributes (warmth, energy, confidence, etc.)

**The Performance Compiler does NOT:**
- Generate audio or phonemes
- Interface directly with models or the Acoustic Backend
- Perform Text-To-Speech (TTS) rendering

## Performance Timeline & Events

A `PerformanceTimeline` is an immutable, chronologically ordered sequence of `PerformanceEvent`s.

### Event Types
- `SPEAK_START`: Marks the beginning of a speech segment.
- `TOKEN`: Represents a single word to be spoken. Contains expressive attributes (all defaulting to 0.5 in v1) and source indices.
- `EMPHASIS`: (Future) Indicates an emphasis modification.
- `PAUSE`: (Future) Indicates a deliberate pause with `duration_ms`.
- `BREATH`: (Future) Indicates a breath (`INHALE` or `EXHALE`).
- `SPEAK_END`: Marks the end of a speech segment.

## Public API

```python
from cse.performance.compiler import (
    compile_performance, 
    validate_timeline, 
    serialize_timeline, 
    deserialize_timeline, 
    get_version
)

# 1. Compile CIR to a Timeline
timeline = compile_performance(cir_document)

# 2. Validate structural integrity
validate_timeline(timeline)

# 3. Serialize to JSON
json_str = serialize_timeline(timeline)

# 4. Deserialize from JSON
restored_timeline = deserialize_timeline(json_str)

# 5. Schema version
print(get_version()) # "1.0.0"
```

## Examples

Given the CIR for `"Hello."`, the compiler generates:
1. `SPEAK_START` at `0ms`
2. `TOKEN` (`"Hello"`) at `0ms` with all attributes set to `0.5`
3. `SPEAK_END` at `150ms`

*Note: In v1.0.0, pacing is strictly deterministic with each token allocating exactly `150ms` of time.*

## Limitations & Future Work

- **Static Defaults**: Currently, all performance attributes (`warmth`, `energy`, etc.) default to `0.5`. There is no ML inference yet.
- **Fixed Timing**: All words take exactly `150ms`. Future versions will implement context-aware dynamic pacing.
- **No Pauses/Breaths**: The current compiler only emits `SPEAK_START`, `TOKEN`, and `SPEAK_END`. Future PRDs will introduce rules to emit `PAUSE` and `BREATH` events natively.
