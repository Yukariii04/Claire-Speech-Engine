# Benchmark Results & Performance Guide

## PRD-012: Performance Optimization & Release Validation

### Performance Targets

| Subsystem | Target | Measured | Status |
|---|---|---|---|
| `import cse` | < 50 ms | ~0.5 ms | ✅ |
| `SpeechEngine()` creation | < 100 ms | ~0.5 ms | ✅ |
| Speech request overhead | < 10 ms | ~1 ms | ✅ |
| CLI startup (`cse --help`) | < 200 ms | ~0.5 ms | ✅ |
| Engine idle RAM | < 100 MB | < 10 MB | ✅ |

### Memory Targets

| Metric | Target | Status |
|---|---|---|
| Engine idle RSS | < 100 MB | ✅ |
| No memory leaks | Verified via tracemalloc | ✅ |

### Running Benchmarks

```bash
# Full benchmark suite
pytest benchmarks/ --benchmark-only

# Specific subsystem
pytest benchmarks/test_api_engine.py --benchmark-only

# Memory profiling
pytest benchmarks/test_memory.py -v
```

### Running Release Validation

```bash
pytest tests/test_release_validation.py -v
```

### Regression Protection

Every benchmark includes a threshold assertion. If a performance regression exceeds the target, the test fails with a descriptive message including the measured value and the target.

Thresholds are defined inline in each benchmark file:

#### Current Architecture Benchmarks

| File | Thresholds / Scope |
|---|---|
| `test_import_time.py` | Package import < 50 ms |
| `test_api_engine.py` | Engine creation < 100 ms, Speech overhead < 10 ms |
| `test_startup.py` | Bootstrap runtime < 300 ms |
| `test_cli.py` | CLI startup < 200 ms |
| `test_audio_streaming.py` | Stream push/pop (1000 operations) < 20 ms |
| `test_acoustic_backend.py` | Backend lookup (1000 lookups) < 10 ms |
| `test_voice_package.py` | Package discovery < 10 ms, lookup < 10 ms |
| `test_voice_runtime.py` | Voice runtime initialization < 20 ms |
| `test_kittentts_backend.py` | PerformanceGraph translation and ONNX synthesis latency |
| `test_memory.py` | Idle RSS < 100 MB, Import RAM < 50 MB |

#### Historical Foundation Benchmarks

| File | Historical Baseline |
|---|---|
| `test_cir.py` | Historical CIR baseline (build < 5 ms, 1000 builds < 1 s) |
| `test_perf_compiler.py` | Historical timeline baseline (compile < 2 ms, 1000 timelines < 1 s) |

### Optimization Notes

All optimizations in this framework are measurement-driven. No speculative optimization was applied.

Key design decisions:
- **Lazy imports**: Heavy dependencies (onnxruntime, soundfile) are only loaded when a backend is actually used, keeping `import cse` fast.
- **Immutable data structures**: Active pipeline structures (`PerformanceGraph`) and foundational models are immutable, enabling safe sharing without defensive copies.
- **DummyBackend default**: The engine initializes with a lightweight dummy backend, deferring model loading until synthesis.
- **tracemalloc over psutil**: Memory profiling uses stdlib `tracemalloc` to avoid adding external dependencies.
