"""CLI Argument Parser (PRD-010, PRD-015 §4-8)."""

import argparse


def create_parser() -> argparse.ArgumentParser:
    """Create the root parser for the CSE CLI."""
    parser = argparse.ArgumentParser(
        prog="cse",
        description="The Claire Speech Engine CLI",
        add_help=True,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # cse help
    subparsers.add_parser("help", help="Show help information")

    # cse version
    subparsers.add_parser("version", help="Show the current version")

    # cse models — list available KittenTTS models
    subparsers.add_parser("models", help="List available KittenTTS models")

    # cse model — model selection and management
    model_parser = subparsers.add_parser("model", help="Model selection and management")
    model_sub = model_parser.add_subparsers(dest="model_command", help="Model subcommands")

    # cse model set <model_id>
    model_set_parser = model_sub.add_parser("set", help="Set model preference")
    model_set_parser.add_argument("model_id", help="Model ID (e.g. kitten-tts-nano-0.8)")

    # cse model current
    model_sub.add_parser("current", help="Show current model selection")

    # cse model reset
    model_sub.add_parser("reset", help="Reset model preference to default")

    # cse voice — interactive voice selection or subcommands
    voice_parser = subparsers.add_parser("voice", help="Voice selection and management")
    voice_sub = voice_parser.add_subparsers(dest="voice_command", help="Voice subcommands")

    # cse voice set <voice>
    set_parser = voice_sub.add_parser("set", help="Set voice preference")
    set_parser.add_argument("voice", help="Voice ID or alias (e.g. Bella or expr-voice-2-f)")

    # cse voice current
    voice_sub.add_parser("current", help="Show current voice selection")

    # cse voice reset
    voice_sub.add_parser("reset", help="Reset voice preference to default")

    # cse example [--force]
    example_parser = subparsers.add_parser("example", help="Copy example scripts into current directory")
    example_parser.add_argument("backend_name", nargs="?", default=None, help="Optional: kittentts")
    example_parser.add_argument("--force", action="store_true", help="Overwrite existing files")

    # cse setup
    subparsers.add_parser("setup", help="Automated setup and pre-download of all KittenTTS models")

    return parser
