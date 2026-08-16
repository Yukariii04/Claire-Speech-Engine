"""Example showing how to generate speech and handle the output."""

import shutil
from pathlib import Path
from cse import SpeechEngine

def main():
    engine = SpeechEngine()
    engine.load_backend("kittentts")
    engine.load_voice("expr-voice-2-f")
    
    # Generate speech
    result = engine.speak("Here is some generated speech that we will move.")
    
    if result.success:
        output_path = Path("output.wav")
        shutil.move(result.audio_path, output_path)
        print(f"Speech saved to {output_path.absolute()}")
    else:
        print("Failed to generate speech")
        
    engine.shutdown()

if __name__ == "__main__":
    main()
