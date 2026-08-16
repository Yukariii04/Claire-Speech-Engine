"""Basic usage of the Claire Speech Engine with KittenTTS."""

from cse import SpeechEngine

def main():
    engine = SpeechEngine()
    engine.load_backend("kittentts")
    engine.load_voice("expr-voice-2-f")
    
    result = engine.speak("Welcome to the Claire Speech Engine.")
    
    if result.success:
        print(f"Success! Audio saved to: {result.audio_path}")
    else:
        print("Failed to generate speech")
        
    engine.shutdown()

if __name__ == "__main__":
    main()
