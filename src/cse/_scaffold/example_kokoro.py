import sys

from cse import SpeechEngine


def main():
    engine = SpeechEngine()
    engine.load_backend("kokoro")
    
    # Configure backend model paths to look in 'models/' if it exists
    from pathlib import Path
    model_dir = Path("models").absolute()
    if model_dir.exists():
        backend = engine._runtime.get_backend()
        from cse.backends.kokoro.config import KokoroConfig
        backend._config = KokoroConfig(
            model_path=model_dir / "kokoro" / "kokoro-v1.0.onnx",
            voices_path=model_dir / "kokoro" / "voices-v1.0.bin",
        )
        backend.shutdown()
        backend.initialize()
    else:
        print("Warning: 'models' directory not found. Assuming models are in current directory.")

    # Read saved voice preference, fall back to af_heart
    from cse.config.user_config import get_preference
    saved_backend = get_preference("backend")
    saved_voice = get_preference("voice")
    if saved_backend == "kokoro" and saved_voice:
        voice = saved_voice
    else:
        voice = sys.argv[1] if len(sys.argv) > 1 else "af_heart"
    engine.load_voice(voice)

    print(f"Kokoro example — using voice '{voice}'.")
    print("Tip: run `cse voices` to see all 54 available voices.\n")

    counter = 1
    while True:
        text = input("Text to speak (empty to quit): ").strip()
        if not text:
            break
        result = engine.speak(text)
        out = f"kokoro_out_{counter}.wav"
        import shutil
        shutil.copy2(str(result.audio_path), out)
        print(f"Saved: {out}")
        counter += 1

    engine.shutdown()
    print("Done.")


if __name__ == "__main__":
    main()
