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


def command_example(args: argparse.Namespace) -> int:
    """Handle 'cse example' — copy scaffold scripts into cwd (RELEASE-002 §2a)."""
    import shutil
    from pathlib import Path

    scaffold_dir = Path(__file__).parent.parent / "_scaffold"
    if not scaffold_dir.exists():
        print("Error: scaffold directory not found. Reinstall claire-speech-engine.")
        return 1

    # ponytail: optional backend filter, otherwise copy all
    target = getattr(args, "backend_name", None)
    force = getattr(args, "force", False)

    all_files = ["example_fishspeech.py", "example_styletts2.py", "example_kokoro.py", "README.md"]
    if target:
        # Copy just the one script + README
        script = f"example_{target}.py"
        if script not in all_files:
            print(f"Unknown backend '{target}'. Available: fishspeech, styletts2, kokoro")
            return 1
        to_copy = [script, "README.md"]
    else:
        to_copy = all_files

    copied = []
    for filename in to_copy:
        src = scaffold_dir / filename
        dst = Path.cwd() / filename
        if dst.exists() and not force:
            print(f"  Skipped {filename} (already exists, use --force to overwrite)")
            continue
        shutil.copy2(str(src), str(dst))
        copied.append(filename)

    if copied:
        print(f"Copied {len(copied)} file(s) to {Path.cwd()}:")
        for f in copied:
            print(f"  {f}")
    else:
        print("Nothing copied (all files already exist).")
    return 0


def command_backends(args: argparse.Namespace) -> int:
    """Handle 'cse backends' — health dashboard (RELEASE-002 §2c)."""
    print("\nInstalled Backends\n")

    backends = [
        ("FishSpeech", "cse.backends.fishspeech.backend", "FishSpeechBackend"),
        ("Kokoro", "cse.backends.kokoro.backend", "KokoroBackend"),
        ("StyleTTS2", "cse.backends.styletts2.backend", "StyleTTS2Backend"),
    ]

    for name, module_path, class_name in backends:
        print(name)
        try:
            import importlib
            mod = importlib.import_module(module_path)
            backend_cls = getattr(mod, class_name)
            backend = backend_cls()
            backend.initialize()

            voices = backend.list_voices()
            caps = backend.get_capabilities()

            print(f"  Status         : Ready")
            print(f"  Voices         : {len(voices)}")
            if hasattr(caps, 'supported_languages'):
                langs = ", ".join(caps.supported_languages)
                print(f"  Languages      : {langs}")
            # ponytail: show default voice if only one
            if len(voices) == 1:
                print(f"  Default Voice  : {voices[0]['id']}")

        except ImportError:
            # ponytail: dependency not installed
            dep = {"FishSpeech": "fish-speech", "Kokoro": "kokoro-onnx", "StyleTTS2": "styletts2"}.get(name, name.lower())
            print(f"  Status         : Missing Dependency")
            print(f"  Reason         : {dep} not installed")
            print(f"  Install        : pip install {dep}")
        except Exception as e:
            print(f"  Status         : Error")
            print(f"  Reason         : {e}")

        print("────────────────────────")

    print()
    return 0
