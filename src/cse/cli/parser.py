"""CLI Argument Parser (PRD-010, PRD-015 §4-8)."""

import argparse


def create_parser() -> argparse.ArgumentParser:
    """Create the root parser for the CSE CLI."""
    parser = argparse.ArgumentParser(
        prog="cse",
        description="The Claire Speech Engine CLI",
        add_help=True
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # cse help
    subparsers.add_parser("help", help="Show help information")
    
    # cse version
    subparsers.add_parser("version", help="Show the current version")
    
    # cse voices — list all voices across all backends
    subparsers.add_parser("voices", help="List available voices for all backends")
    
    # cse voice — interactive selection or subcommands
    voice_parser = subparsers.add_parser("voice", help="Voice selection and management")
    voice_sub = voice_parser.add_subparsers(dest="voice_command", help="Voice subcommands")
    
    # cse voice set <backend> <voice>
    set_parser = voice_sub.add_parser("set", help="Set voice preference")
    set_parser.add_argument("backend", help="Backend ID (kokoro, styletts2)")
    set_parser.add_argument("voice", help="Voice ID")
    
    # cse voice current
    voice_sub.add_parser("current", help="Show current voice selection")
    
    # cse voice reset
    voice_sub.add_parser("reset", help="Reset voice preference to defaults")
    


    # cse example [backend] [--force]
    example_parser = subparsers.add_parser("example", help="Copy example scripts into current directory")
    example_parser.add_argument("backend_name", nargs="?", default=None,
                                help="Optional: styletts2 or kokoro")
    example_parser.add_argument("--force", action="store_true", help="Overwrite existing files")

    # cse setup <backend>
    setup_parser = subparsers.add_parser("setup", help="Automated setup and model download for a backend")
    setup_parser.add_argument("backend_name", help="styletts2 or kokoro")

    # cse backends
    subparsers.add_parser("backends", help="Show installed backend status dashboard")

    return parser
