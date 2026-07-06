# Claire Intermediate Representation (CIR)

## What is CIR?

The **Claire Intermediate Representation (CIR)** is the canonical, immutable internal representation of all language entering the Claire Speech Engine (CSE). 

Instead of passing raw text strings between different modules (which leads to redundant parsing, inconsistent tokenization, and lost metadata), CSE parses text exactly once into a `CIRDocument` at the very beginning of the pipeline.

**CIR is NOT:**
- A parser (it relies on simple regex-based tokenization for now)
- A grammar tree
- A phoneme or pronunciation generator

**CIR IS:**
- An immutable, versioned data model
- Optimized for downstream expressive speech generation
- Fully serializable (JSON) for debugging and caching

## Why does CSE use CIR?

By forcing every downstream system to consume CIR instead of raw text, we achieve:
1. **Determinism**: Every token and segment gets a UUID seeded from its text and offset, ensuring reproducible execution across runs.
2. **Immutability**: Once a document is built, it cannot be modified. Downstream modules (like Performance Compiler or Voice Runtime) must create new IRs or attach annotations, rather than mutating the original text.
3. **Traceability**: Because every element has a UUID and metadata (like source offsets), any error in speech generation can be traced exactly back to the source text.

## Architecture & Object Hierarchy

```
CIRDocument
    │
    └── CIRUtterance (Typically a sentence)
            │
            └── CIRSpeechSegment (Smallest performance unit)
                    │
                    └── CIRLexicalToken (Individual words + punctuation)
```

- `CIRDocument`: Top-level container representing a single input payload.
- `CIRUtterance`: Represents a single spoken utterance (sentence boundary).
- `CIRSpeechSegment`: The smallest meaningful performance unit. Currently 1:1 with Utterance, but built for future prosody/emotion chunking.
- `CIRLexicalToken`: A single lexical element (word) with its trailing whitespace and punctuation separated.

## Public API

The `cse.language.cir` package intentionally exposes a minimal API:

```python
from cse.language.cir import build_cir, validate, serialize, deserialize, get_version

# 1. Get the current schema version
version = get_version()  # e.g., "2.0.0"

# 2. Parse text into an immutable document
doc = build_cir("I really missed you.")

# 3. Validate a document's structural integrity
validate(doc)  # Raises CIRValidationError if invalid

# 4. Serialize to JSON for storage/transport
json_str = serialize(doc)

# 5. Restore from JSON
restored_doc = deserialize(json_str)
```

## Example Structure

```json
{
  "uuid": "a1b2c3d4-...",
  "version": "2.0.0",
  "raw_text": "I really missed you.",
  "language": "en",
  "utterances": [
    {
      "uuid": "...",
      "text": "I really missed you.",
      "segments": [
        {
          "uuid": "...",
          "text": "I really missed you.",
          "tokens": [
            {
              "uuid": "...",
              "text": "I",
              "normalized": "i",
              "position": 0,
              "source_offset": 0,
              "length": 1,
              "whitespace_after": " ",
              "punctuation_after": ""
            }
            // ... "really", "missed", "you"
          ],
          "segment_index": 0,
          "source_offset": 0,
          "length": 20,
          "metadata": { ... }
        }
      ],
      "metadata": { ... }
    }
  ],
  "metadata": { ... }
}
```

## Limitations & Future Work

- **No Emotion or Prosody**: CIR explicitly forbids emotion, prosody, and timing tags. Those belong in the future Performance IR.
- **No Phonemes**: Lexical tokens represent orthographic text only.
- **English UTF-8 Only**: The builder currently only splits sentences and tokens based on English punctuation heuristics.
- **No Streaming**: CIR is a discrete document model, designed for complete payloads, not chunked streaming inputs.
