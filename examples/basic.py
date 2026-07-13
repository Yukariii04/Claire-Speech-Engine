"""Basic usage of the Claire Speech Engine."""

from cse import SpeechEngine

def main():
    engine = SpeechEngine()
    
    print("Loading backend 'kokoro'...")
    engine.load_backend("kokoro")
    
    print("Loading voice 'af_heart'...")
    engine.load_voice("af_heart")
    
    print("Generating speech...")
    speech = engine.speak("Hello!")
    
    if speech.success:
        print(f"Success! Audio saved to: {speech.audio_path}")
    else:
        print("Speech generation failed.")
        
    engine.shutdown()

if __name__ == "__main__":
    main()
