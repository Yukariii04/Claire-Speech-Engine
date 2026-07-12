"""Claire Speech Engine — Entry Point."""

if __name__ == "__main__":
    import sys
    from pathlib import Path

    # Swap the script's directory for src/ so Python resolves the package
    _here = str(Path(__file__).resolve().parent)
    _src = str(Path(_here) / "src")

    sys.path = [_src] + [p for p in sys.path if p not in (_here, "", ".")]
    sys.modules.pop("cse", None)

    from cse.cli.main import main

    sys.exit(main())
