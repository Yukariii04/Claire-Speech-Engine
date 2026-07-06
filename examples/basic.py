"""Basic usage of the Claire Speech Engine."""

from cse import SpeechEngine

def main():
    engine = SpeechEngine()
    
    print("Loading voice 'claire'...")
    # fallback to 'af_heart' since 'claire' might just be a dummy in tests
    # or you can assume 'claire' is installed
    engine.load_voice("claire")
    
    print("Generating speech...")
    speech = engine.speak("Hello from The Claire Speech Engine.")
    
    if speech.success:
        print(f"Success! Audio saved to: {speech.audio_path}")
    else:
        print("Speech generation failed.")
        
    engine.shutdown()

if __name__ == "__main__":
    main()
