from cse import SpeechEngine


def main():
    engine = SpeechEngine()
    engine.load_backend("styletts2")
    
    # Configure backend model paths to look in 'models/' if it exists
    from pathlib import Path
    model_dir = Path("models").absolute()
    if model_dir.exists():
        backend = engine._runtime.get_backend()
        from cse.backends.styletts2.config import StyleTTS2Config
        backend._config = StyleTTS2Config(
            model_dir=model_dir / "styletts2"
        )
        backend.shutdown()
        backend.initialize()
    else:
        print("Warning: 'models' directory not found. Assuming models are in current directory.")

    # Read saved voice preference only if it was set for styletts2
    from cse.config.user_config import get_preference
    saved_backend = get_preference("backend")
    saved_voice = get_preference("voice")
    voice = saved_voice if saved_backend == "styletts2" and saved_voice else "claire_neutral"
    engine.load_voice(voice)

    print("StyleTTS2 example — type text to synthesize, empty line to quit.")
    print("Tip: run `cse voices` to see all available voices.\n")

    counter = 1
    while True:
        text = input("Text to speak (empty to quit): ").strip()
        if not text:
            break
        result = engine.speak(text)
        out = f"styletts2_out_{counter}.wav"
        import shutil
        shutil.copy2(str(result.audio_path), out)
        print(f"Saved: {out}")
        counter += 1

    engine.shutdown()
    print("Done.")


if __name__ == "__main__":
    main()
