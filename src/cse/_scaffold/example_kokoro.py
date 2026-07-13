import sys

from cse import SpeechEngine


def main():
    engine = SpeechEngine()
    engine.load_backend("kokoro")

    # ponytail: optionally accept a voice id from argv, default af_heart
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
