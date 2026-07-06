"""CLI Commands implementation (PRD-010)."""

import argparse
import sys
from cse.api.exceptions import SpeechEngineError

def command_version(args: argparse.Namespace) -> int:
    """Handle 'cse version' command."""
    from cse import SpeechEngine
    engine = SpeechEngine()
    print(f"Claire Speech Engine {engine.get_version()}")
    engine.shutdown()
    return 0

def command_voices(args: argparse.Namespace) -> int:
    """Handle 'cse voices' command."""
    from cse import SpeechEngine
    engine = SpeechEngine()
    voices = engine.list_voices()
    
    if not voices:
        print("No voices found.")
    else:
        for voice in voices:
            print(f"- {voice}")
            
    engine.shutdown()
    return 0

def command_speak(args: argparse.Namespace) -> int:
    """Handle 'cse speak' command."""
    from cse import SpeechEngine
    engine = SpeechEngine()
    try:
        engine.load_voice(args.voice)
        result = engine.speak(args.text)
        if result.success:
            print(f"Speech generated successfully: {result.audio_path}")
            return 0
        else:
            print("Failed to generate speech.")
            return 1
    except SpeechEngineError as e:
        print(f"Error: {e}")
        return 1
    finally:
        engine.shutdown()
