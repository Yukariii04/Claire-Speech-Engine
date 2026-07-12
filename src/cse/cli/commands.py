"""CLI Commands implementation (PRD-010, PRD-015 §4-8)."""

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
    """Handle 'cse voices' — list voices from all backends (PRD-015 §4)."""
    from cse.runtime.voice.runtime import VoiceRuntime

    for backend_id in VoiceRuntime.available_backend_ids():
        print(f"\n{'=' * 50}")
        print(f"  {backend_id.upper()}")
        print(f"{'=' * 50}\n")

        try:
            # ponytail: instantiate backend directly, no full engine init needed
            if backend_id == "kokoro":
                from cse.backends.kokoro.backend import KokoroBackend
                backend = KokoroBackend()
            elif backend_id == "fishspeech":
                from cse.backends.fishspeech.backend import FishSpeechBackend
                backend = FishSpeechBackend()
            elif backend_id == "styletts2":
                from cse.backends.styletts2.backend import StyleTTS2Backend
                backend = StyleTTS2Backend()
            else:
                continue

            voices = backend.list_voices()
            if not voices:
                print("  (no voices found)")
            else:
                for v in voices:
                    parts = [f"{v['id']:<16}", v.get("name", ""), v.get("language", ""), v.get("gender", "")]
                    print("  " + "  ".join(p for p in parts if p))
        except Exception as e:
            print(f"  (error loading backend: {e})")

    print()
    return 0


def command_voice(args: argparse.Namespace) -> int:
    """Handle 'cse voice' — interactive selection or subcommands (PRD-015 §5-8)."""
    from cse.config.user_config import get_preference, set_preference, clear_preferences

    sub = getattr(args, "voice_command", None)

    if sub == "current":
        backend = get_preference("backend")
        voice = get_preference("voice")
        if not backend and not voice:
            print("No voice preference saved. Using backend defaults.")
        else:
            print(f"Backend : {backend or '(not set)'}")
            print(f"Voice   : {voice or '(not set)'}")
        return 0

    if sub == "reset":
        clear_preferences()
        print("Voice preference reset. Using backend defaults.")
        return 0

    if sub == "set":
        backend_id = args.backend
        voice_id = args.voice

        # Validate the backend exists
        from cse.runtime.voice.runtime import VoiceRuntime
        valid_backends = VoiceRuntime.available_backend_ids()
        if backend_id not in valid_backends:
            print(f'Unknown backend "{backend_id}". Available: {", ".join(valid_backends)}')
            return 1

        # Validate voice belongs to backend
        if backend_id == "kokoro":
            from cse.backends.kokoro.backend import KokoroBackend
            backend = KokoroBackend()
        elif backend_id == "fishspeech":
            from cse.backends.fishspeech.backend import FishSpeechBackend
            backend = FishSpeechBackend()
        elif backend_id == "styletts2":
            from cse.backends.styletts2.backend import StyleTTS2Backend
            backend = StyleTTS2Backend()
        else:
            print(f"Unknown backend: {backend_id}")
            return 1

        if not backend.validate_voice(voice_id):
            voices = backend.list_voices()
            voice_list = ", ".join(v["id"] for v in voices)
            print(f'Voice "{voice_id}" is not available for {backend_id}.')
            print(f"Available: {voice_list}")
            return 1

        set_preference("backend", backend_id)
        set_preference("voice", voice_id)
        print(f"\nSelected\n")
        print(f"  Backend : {backend_id}")
        print(f"  Voice   : {voice_id}")
        print(f"\n✓ Saved")
        return 0

    # No subcommand → interactive selection (PRD-015 §5)
    from cse.runtime.voice.runtime import VoiceRuntime
    backend_ids = VoiceRuntime.available_backend_ids()

    print("\nSelect Backend\n")
    for i, bid in enumerate(backend_ids, 1):
        print(f"  {i}) {bid.title()}")
    print()

    try:
        choice = input("> ")
        idx = int(choice) - 1
        if idx < 0 or idx >= len(backend_ids):
            print("Invalid selection.")
            return 1
    except (ValueError, EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        return 1

    backend_id = backend_ids[idx]

    # Instantiate to get voices
    if backend_id == "kokoro":
        from cse.backends.kokoro.backend import KokoroBackend
        backend = KokoroBackend()
    elif backend_id == "fishspeech":
        from cse.backends.fishspeech.backend import FishSpeechBackend
        backend = FishSpeechBackend()
    elif backend_id == "styletts2":
        from cse.backends.styletts2.backend import StyleTTS2Backend
        backend = StyleTTS2Backend()
    else:
        return 1

    voices = backend.list_voices()
    print(f"\nAvailable {backend_id.title()} Voices\n")
    for i, v in enumerate(voices, 1):
        print(f"  {i}) {v['id']}")
    print()

    try:
        choice = input("> ")
        idx = int(choice) - 1
        if idx < 0 or idx >= len(voices):
            print("Invalid selection.")
            return 1
    except (ValueError, EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        return 1

    voice_id = voices[idx]["id"]
    set_preference("backend", backend_id)
    set_preference("voice", voice_id)

    print(f"\nSelected\n")
    print(f"  Backend : {backend_id}")
    print(f"  Voice   : {voice_id}")
    print(f"\n✓ Saved")
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
