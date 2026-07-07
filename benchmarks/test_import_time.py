def test_import_time_direct(benchmark):
    """Import cse must complete in < 50ms (PRD-012 §3)."""
    def import_cse_direct():
        import sys
        sys.modules.pop("cse", None)
        import cse
    benchmark(import_cse_direct)
    assert benchmark.stats["mean"] < 0.050, (
        f"Import mean {benchmark.stats['mean']:.4f}s exceeds 50ms target"
    )
