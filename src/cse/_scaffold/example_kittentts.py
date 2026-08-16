"""KittenTTS interactive speech synthesis example."""

import sys
from pathlib import Path
from cse import SpeechEngine
from cse.config.user_config import get_preference

def main():
    engine = SpeechEngine()
    engine.load_backend("kittentts")

    # Read voice from args, saved preference, or backend default
    saved_backend = get_preference("backend")
    saved_voice = get_preference("voice")
    
    if len(sys.argv) > 1:
        voice = sys.argv[1]
    elif saved_backend == "kittentts" and saved_voice:
        voice = saved_voice
    else:
        voice = "expr-voice-2-f"

    try:
        engine.load_voice(voice)
    except Exception as e:
        print(f"Error loading voice '{voice}': {e}")
        engine.shutdown()
        sys.exit(1)

    print(f"KittenTTS example — Voice: {voice}")
    print("Type text to synthesize, or empty line to quit.\n")

    counter = 1
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not line:
            break

        result = engine.speak(line)
        if result.success:
            print(f"  -> Generated: {result.audio_path} ({result.duration_seconds:.2f}s)")
            counter += 1
        else:
            print("  -> Synthesis failed.")

    engine.shutdown()

if __name__ == "__main__":
    main()
