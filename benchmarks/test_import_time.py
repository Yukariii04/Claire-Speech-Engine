def test_import_time_direct(benchmark):
    def import_cse_direct():
        import sys
        sys.modules.pop("cse", None)
        import cse
    benchmark(import_cse_direct)
