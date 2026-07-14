###############################################################################
#
#                           THE CLAIRE PROJECT
#
#                            Project Lexicon
#
# Document Number : LEXICON-001
# Title           : Claire Lexicon
# Version         : 1.0.0
# Status          : Ratified
#
###############################################################################
````

# 1. Purpose

The Claire Lexicon defines the official terminology of the Claire Project.

Its purpose is to ensure that all future documentation, research, architecture, implementation, and discussions use a consistent vocabulary.

Every subsequent document SHALL use the terminology defined herein.

-------------------------------------------------------------------------------

# 2. Core Terms

## Claire Project

The complete research and engineering initiative consisting of CSE, CPE, and CAM.

---

## Claire Speech Engine (CSE)

The backend-agnostic framework responsible for speech generation infrastructure.

Responsibilities include:

- Public API
- Runtime
- Backend abstraction
- CLI
- Voice management
- Streaming
- Packaging

CSE does not perform communication reasoning.

---

## Claire Performance Engine (CPE)

The communication intelligence layer.

CPE transforms text and optional contextual information into a backend-independent representation of speech performance.

CPE never generates audio.

---

## Claire Acoustic Model (CAM)

The native acoustic renderer of the Claire Project.

CAM converts performance representations into speech.

CAM performs no communication reasoning.

---

## Compatible Backend

Any acoustic backend supported by CSE other than Claire.

Examples include Kokoro and StyleTTS2.

Compatible backends reproduce as much of the Performance Graph as their capabilities permit.

---

## Reference Backend

Claire.

The reference implementation of the complete CPE specification.

All new expressive capabilities are designed with Claire as the reference backend.

-------------------------------------------------------------------------------

# 3. Performance Terms

## Performance Context

The complete input supplied to CPE.

Contains:

Required:

```text
Text
```

Optional:

```text
Character State
```

Future versions may introduce additional optional context without changing the core architecture.

---

## Character State

The current emotional condition of the speaker.

Examples:

- Happy
- Sad
- Angry
- Sleepy
- Curious

Character State influences speech performance but does not determine it completely.

---

## Meaning

The semantic content expressed by the text.

Meaning answers:

> "What does the sentence literally communicate?"

---

## Intent

The communicative purpose behind the sentence.

Intent answers:

> "Why is the speaker saying this?"

---

## Performance

The manner in which speech should be delivered.

Performance is independent of every acoustic model.

Examples include:

- Energy
- Warmth
- Confidence
- Hesitation
- Rhythm
- Emphasis

Performance does not describe implementation details.

---

## Performance Graph

The immutable backend-independent representation produced by CPE.

The Performance Graph describes how speech should be performed.

It contains no backend-specific information.

---

## Translator

The component responsible for converting a Performance Graph into backend-specific instructions.

Each backend owns its own translator.

-------------------------------------------------------------------------------

# 4. Architecture Terms

## Backend

A speech synthesis implementation compatible with CSE.

---

## Backend Capability

A feature supported by a backend.

Examples include:

- Emotion
- Style
- Voice selection
- Streaming

Backends may support different capability sets.

---

## Capability Degradation

The process by which a backend approximates unsupported portions of the Performance Graph.

Capability degradation is expected behavior and not considered an error.

-------------------------------------------------------------------------------

# 5. Research Terms

## RFD

Research Foundation Document.

Defines research vision, terminology, or methodology.

---

## ADR

Architecture Decision Record.

Documents important architectural decisions.

---

## PRD

Product Requirements Document.

Defines implementation requirements.

---

## Constitution

The highest-level governance document of the Claire Project.

All other documentation SHALL conform to its principles.

-------------------------------------------------------------------------------

# 6. Guiding Principle

Whenever ambiguity exists, the definitions contained in this Lexicon take precedence over informal terminology.

Future documents SHALL extend this Lexicon rather than redefine existing terminology.

-------------------------------------------------------------------------------

# 7. Status

Version:

```text
1.0
```

Status:

```text
Ratified
```

-------------------------------------------------------------------------------

# 8. AI Instructions

Before creating future project documentation:

1. Read the Claire Project Constitution.
2. Read this Lexicon.
3. Use the terminology defined herein.
4. Do not redefine existing terms.
5. Extend this Lexicon only when introducing genuinely new project concepts.

All future documentation SHALL use these definitions consistently.

###############################################################################

END OF LEXICON-001

###############################################################################