from cse import SpeechEngine


def main():
    engine = SpeechEngine()
    engine.load_backend("fishspeech")
    engine.load_voice()

    print("Fish Speech example — type text to synthesize, empty line to quit.")
    print("Tip: run `cse voices` to see all available voices.\n")

    counter = 1
    while True:
        text = input("Text to speak (empty to quit): ").strip()
        if not text:
            break
        result = engine.speak(text)
        # ponytail: simple incrementing filenames in cwd
        out = f"fishspeech_out_{counter}.wav"
        import shutil
        shutil.copy2(str(result.audio_path), out)
        print(f"Saved: {out}")
        counter += 1

    engine.shutdown()
    print("Done.")


if __name__ == "__main__":
    main()
