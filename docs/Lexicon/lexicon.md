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

The complete speech engine system consisting of CPE (performance/communication reasoning), CAM (acoustic rendering), and supporting runtime/infrastructure.

Responsibilities include:

- Public API
- Runtime lifecycle
- Voice and model management
- Streaming audio transport
- CLI tools
- Packaging and distribution

CSE coordinates the flow from text to performance reasoning to acoustic speech output.

---

## Claire Performance Engine (CPE)

The performance and communication reasoning layer of the Claire Project.

CPE transforms text and optional contextual information (Character State) into an immutable, backend-independent PerformanceGraph.

CPE never generates audio.

---

## Claire Acoustic Model (CAM)

The native acoustic rendering layer of the Claire Project.

CAM converts the PerformanceGraph produced by CPE directly into natural speech.

CAM performs no communication reasoning.

---

## Compatible Backend

An optional acoustic implementation that can consume the CPE PerformanceGraph while satisfying the CAM contract.

Compatible backends are not peer architectures to CAM; they serve as interim or alternative acoustic renderers (such as KittenTTS) that adapt and approximate the PerformanceGraph via translation.

---

## Reference Backend

Claire / CAM (Claire Acoustic Model).

The native and intended acoustic model of CSE, designed to render the complete PerformanceGraph specification directly into speech.

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

The immutable, backend-independent representation produced by CPE and consumed by CAM.

The Performance Graph describes how speech should be performed (intent, semantics, and expressive delivery plan) and serves as the definitive contract between CPE and CAM.

Compatible acoustic implementations may also consume the Performance Graph when satisfying the CAM contract.

It contains no backend-specific commands.

---

## Translator

The adapter component responsible for converting a Performance Graph into backend-specific instructions for compatible backends.

Each compatible backend implements its own translator (subclassing `BaseTranslator`).

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