"""CLI Argument Parser (PRD-010)."""

import argparse
import sys

def create_parser() -> argparse.ArgumentParser:
    """Create the root parser for the CSE CLI."""
    parser = argparse.ArgumentParser(
        prog="cse",
        description="The Claire Speech Engine CLI",
        add_help=True
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # cse help
    help_parser = subparsers.add_parser("help", help="Show help information")
    
    # cse version
    version_parser = subparsers.add_parser("version", help="Show the current version")
    
    # cse voices
    voices_parser = subparsers.add_parser("voices", help="List available voices")
    
    # cse speak
    speak_parser = subparsers.add_parser("speak", help="Generate speech from text")
    speak_parser.add_argument("--voice", required=True, help="Voice ID to use (e.g., 'claire')")
    speak_parser.add_argument("--text", required=True, help="Text to speak")
    
    return parser
