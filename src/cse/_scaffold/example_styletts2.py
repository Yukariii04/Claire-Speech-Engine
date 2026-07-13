from cse import SpeechEngine


def main():
    engine = SpeechEngine()
    engine.load_backend("styletts2")
    engine.load_voice()

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
