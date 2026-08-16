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


def command_models(args: argparse.Namespace) -> int:
    """Handle 'cse models' — list available KittenTTS models."""
    from cse.backends.kittentts.backend import list_models
    from cse.config.user_config import get_preference

    active_model = get_preference("model") or "kitten-tts-nano-0.8"
    models = list_models()

    print("\nAvailable KittenTTS Models\n")
    print(f"  {'ID':<25} {'Name':<25} {'Size / Parameters':<25} {'Status'}")
    print(f"  {'-' * 25} {'-' * 25} {'-' * 25} {'-' * 10}")

    for m in models:
        is_active = (m["id"] == active_model or m["repo_id"] == active_model)
        status = "Active (*)" if is_active else "Available"
        print(f"  {m['id']:<25} {m['name']:<25} {m['size']:<25} {status}")
    print()
    return 0


def command_model(args: argparse.Namespace) -> int:
    """Handle 'cse model' — interactive model selection or subcommands."""
    from cse.backends.kittentts.backend import list_models, validate_model
    from cse.config.user_config import get_preference, set_preference

    sub = getattr(args, "model_command", None)

    if sub == "current":
        current = get_preference("model") or "kitten-tts-nano-0.8 (default)"
        print(f"Active Model : {current}")
        return 0

    if sub == "reset":
        set_preference("model", "kitten-tts-nano-0.8")
        print("Model preference reset to default (kitten-tts-nano-0.8).")
        return 0

    if sub == "set":
        model_id = args.model_id
        if not validate_model(model_id):
            models = list_models()
            available = ", ".join(m["id"] for m in models)
            print(f'Model "{model_id}" is not valid.')
            print(f"Available: {available}")
            return 1

        set_preference("model", model_id)
        print(f"\nSelected Model: {model_id}")
        print("Saved\n")
        return 0

    # Interactive selection
    models = list_models()
    current = get_preference("model") or "kitten-tts-nano-0.8"
    print("\nSelect KittenTTS Model\n")
    for i, m in enumerate(models, 1):
        marker = " (current)" if (m["id"] == current or m["repo_id"] == current) else ""
        print(f"  {i}) {m['name']} [{m['id']}] - {m['size']}{marker}")
    print()

    try:
        choice = input("> ")
        idx = int(choice) - 1
        if idx < 0 or idx >= len(models):
            print("Invalid selection.")
            return 1
    except (ValueError, EOFError, KeyboardInterrupt):
        print("\nCancelled.")
        return 1

    selected = models[idx]["id"]
    set_preference("model", selected)
    print(f"\nSelected Model: {selected}")
    print("Saved\n")
    return 0


def command_voice(args: argparse.Namespace) -> int:
    """Handle 'cse voice' — interactive selection or subcommands."""
    from cse.backends.kittentts.backend import KittenTTSBackend
    from cse.config.user_config import get_preference, set_preference, clear_preferences

    sub = getattr(args, "voice_command", None)

    if sub == "current":
        voice = get_preference("voice")
        if not voice:
            print("No voice preference saved. Using default (expr-voice-2-f / Bella).")
        else:
            print(f"Active Voice : {voice}")
        return 0

    if sub == "reset":
        set_preference("voice", "expr-voice-2-f")
        print("Voice preference reset to default (expr-voice-2-f / Bella).")
        return 0

    if sub == "set":
        raw_voice = args.voice
        backend = KittenTTSBackend()
        if not backend.validate_voice(raw_voice):
            voices = backend.list_voices()
            voice_list = ", ".join(f"{v['id']} ({v['alias']})" for v in voices)
            print(f'Voice "{raw_voice}" is not valid.')
            print(f"Available voices: {voice_list}")
            return 1

        set_preference("backend", "kittentts")
        set_preference("voice", raw_voice)
        print(f"\nSelected Voice: {raw_voice}")
        print("Saved\n")
        return 0

    # Interactive selection (direct voice list — no backend prompt needed)
    backend = KittenTTSBackend()
    voices = backend.list_voices()
    current_voice = get_preference("voice") or "expr-voice-2-f"

    print("\nSelect KittenTTS Voice\n")
    for i, v in enumerate(voices, 1):
        is_current = (
            v["id"].lower() == current_voice.lower()
            or v.get("alias", "").lower() == current_voice.lower()
        )
        marker = " (current)" if is_current else ""
        print(f"  {i}) {v['id']} ({v['alias']}){marker}")
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

    selected = voices[idx]["id"]
    set_preference("backend", "kittentts")
    set_preference("voice", selected)

    print(f"\nSelected Voice: {selected}")
    print("Saved\n")
    return 0


def command_example(args: argparse.Namespace) -> int:
    """Handle 'cse example' — copy scaffold scripts into cwd."""
    import shutil
    from pathlib import Path

    scaffold_dir = Path(__file__).parent.parent / "_scaffold"
    if not scaffold_dir.exists():
        print("Error: scaffold directory not found. Reinstall claire-speech-engine.")
        return 1

    target = getattr(args, "backend_name", None)
    force = getattr(args, "force", False)

    all_files = ["example_kittentts.py", "README.md"]
    if target:
        script = f"example_{target}.py"
        if script not in all_files:
            print(f"Unknown backend '{target}'. Available: kittentts")
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


def command_setup(args: argparse.Namespace) -> int:
    """Handle 'cse setup' — automated installer and pre-downloader for all KittenTTS models."""
    import subprocess
    import sys
    from cse.backends.kittentts.backend import download_all_models

    print("Installing/verifying KittenTTS dependencies...")
    wheel_url = "https://github.com/KittenML/KittenTTS/releases/download/0.8.1/kittentts-0.8.1-py3-none-any.whl"
    proc = subprocess.run([sys.executable, "-m", "pip", "install", wheel_url, "soundfile"])
    if proc.returncode != 0:
        print(f"\nError: Dependency installation failed with exit code {proc.returncode}.")
        return 1

    print("\nPre-downloading all supported KittenTTS models for offline use...")
    try:
        failed_models = download_all_models()
    except Exception as e:
        print(f"\nError: Model download encountered an issue: {e}")
        return 1

    if failed_models:
        print(f"\nError: Failed to pre-download {len(failed_models)} model(s): {', '.join(failed_models)}")
        print("Models will be downloaded automatically on first use.")
        return 1

    print("\nAll KittenTTS models successfully downloaded and ready!")
    return 0
