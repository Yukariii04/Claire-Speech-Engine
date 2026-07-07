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

| File | Thresholds |
|---|---|
| `test_import_time.py` | Import < 50 ms |
| `test_api_engine.py` | Engine creation < 100 ms, Speech overhead < 10 ms |
| `test_startup.py` | Bootstrap < 300 ms |
| `test_cli.py` | CLI startup < 200 ms |
| `test_cir.py` | CIR build < 5 ms, 1000 builds < 1 s |
| `test_perf_compiler.py` | Compile < 2 ms, 1000 timelines < 1 s |
| `test_audio_streaming.py` | 1000 push/pop < 20 ms |
| `test_acoustic_backend.py` | 1000 lookups < 10 ms |
| `test_voice_package.py` | Discovery < 10 ms, 1000 lookups < 10 ms |
| `test_voice_runtime.py` | Initialization < 20 ms |
| `test_memory.py` | Idle < 100 MB, Import < 50 MB |

### Optimization Notes

All optimizations in this PRD are measurement-driven. No speculative optimization was applied.

Key design decisions:
- **Lazy imports**: Heavy dependencies (torch, onnxruntime) are only loaded when a backend is actually used, keeping `import cse` fast.
- **Immutable data structures**: CIR and PerformanceTimeline are immutable, enabling safe sharing without defensive copies.
- **DummyBackend default**: The engine initializes with a lightweight dummy backend, deferring model loading until `load_voice()`.
- **tracemalloc over psutil**: Memory profiling uses stdlib `tracemalloc` to avoid adding a dependency.
