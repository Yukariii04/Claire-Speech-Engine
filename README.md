# Claire Speech Engine (CSE)

> Production-grade speech synthesis foundation.

---

## Project Goals

Claire Speech Engine is a modular, production-grade speech synthesis engine built in Python. This repository establishes the engineering foundation — packaging, configuration, logging, module discovery, and runtime lifecycle — upon which future speech features will be built.

**Current milestone:** PRD-001 — Project Bootstrap & Foundation (no speech features yet).

---

## Installation

**Requirements:** Python ≥ 3.12

```bash
git clone <repo-url> ClaireSpeechEngine
cd ClaireSpeechEngine
pip install -e ".[dev]"
```

---

## Running

```bash
python cse.py
```

**Expected output:**

```text
Claire Speech Engine
Version 0.1.0

Configuration Loaded
Logger Initialized
Module Registry Initialized
Runtime Ready
```

### CLI Options

| Flag        | Description              |
|-------------|--------------------------|
| `--help`    | Show usage information   |
| `--version` | Print version and exit   |
| `--debug`   | Enable debug-level logs  |

---

## Repository Structure

```text
ClaireSpeechEngine/
├── docs/                  # Documentation
│   ├── PRDs/              # Product requirements
│   ├── RFCs/              # Design proposals
│   ├── Architecture/      # Architecture docs
│   └── Benchmarks/        # Benchmark reports
├── src/cse/               # Source code
│   ├── api/               # Public API surface
│   ├── config/            # Configuration system
│   ├── core/              # Logger, registry
│   ├── runtime/           # Bootstrap & lifecycle
│   ├── plugins/           # Plugin interface
│   ├── performance/       # Profiling utilities
│   ├── speech/            # (future) Speech modules
│   ├── prosody/           # (future) Prosody modules
│   ├── streaming/         # (future) Streaming modules
│   ├── models/            # (future) Model definitions
│   └── utils/             # Shared helpers
├── tests/                 # Test suite
├── benchmarks/            # Performance benchmarks
├── configs/               # YAML configuration files
├── examples/              # Usage examples
├── assets/                # Static assets
├── models/                # Trained model weights
├── scripts/               # Dev & build scripts
├── training/              # Training pipelines
└── third_party/           # Vendored dependencies
```

---

## Development

### Running Tests

```bash
pytest
```

### Running Benchmarks

```bash
pytest benchmarks/ --benchmark-only
```

### Configuration

Default config lives at `configs/default.yaml`. Override any value with environment variables using the `CSE_` prefix:

```bash
CSE_RUNTIME_DEBUG=true python cse.py
```

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Ensure all tests pass (`pytest`)
4. Ensure code style compliance (pre-commit hooks handle this)
5. Submit a pull request

### Coding Standards

- PEP 8 compliance
- Type hints on all public functions
- Docstrings on all public functions and classes
- No global mutable state
- Dependency injection where appropriate
- No circular imports
