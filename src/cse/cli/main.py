"""CLI Main Entry Point (PRD-010, PRD-015)."""

import sys
import argparse
from cse.cli.parser import create_parser
from cse.cli import commands

def main() -> int:
    """Main CLI routing."""
    parser = create_parser()
    
    # Handle `cse help` -> treat as `cse --help`
    if len(sys.argv) > 1 and sys.argv[1] == "help":
        parser.print_help()
        return 0
        
    args = parser.parse_args()
    
    if args.command == "version":
        return commands.command_version(args)
    elif args.command == "voices":
        return commands.command_voices(args)
    elif args.command == "voice":
        return commands.command_voice(args)
    elif args.command == "speak":
        return commands.command_speak(args)
    elif args.command == "example":
        return commands.command_example(args)
    elif args.command == "setup":
        return commands.command_setup(args)
    elif args.command == "backends":
        return commands.command_backends(args)
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())
