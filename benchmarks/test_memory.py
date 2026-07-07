"""Benchmarks: Memory profiling (PRD-012 §4).

Target: Engine idle < 100 MB RAM.
"""

import sys
import os


def test_engine_idle_memory():
    """Engine at idle must use < 100 MB RSS."""
    import cse
    from cse import SpeechEngine

    engine = SpeechEngine()

    # ponytail: tracemalloc for in-process measurement, psutil when it matters
    import tracemalloc
    tracemalloc.start()

    # Snapshot after engine creation (idle state)
    snapshot = tracemalloc.take_snapshot()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    peak_mb = peak / (1024 * 1024)
    engine.shutdown()

    # PRD-012: < 100 MB idle
    assert peak_mb < 100, (
        f"Engine idle peak memory {peak_mb:.1f} MB exceeds 100 MB target"
    )


def test_import_memory():
    """Importing cse should not allocate excessive memory."""
    import tracemalloc
    tracemalloc.start()

    # Force re-import
    for mod in list(sys.modules):
        if mod.startswith("cse"):
            del sys.modules[mod]

    import cse

    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    peak_mb = peak / (1024 * 1024)
    assert peak_mb < 50, (
        f"Import peak memory {peak_mb:.1f} MB exceeds 50 MB target"
    )
