"""Example showing how to generate speech and handle the output."""

import shutil
from pathlib import Path
from cse import SpeechEngine

def main():
    engine = SpeechEngine()
    engine.load_voice("claire")
    
    # Generate speech
    result = engine.speak("Here is some generated speech that we will move.")
    
    if result.success:
        output_path = Path("output.wav")
        # The engine saves to a temp dir by default. 
        # Move it to our desired location.
        shutil.move(result.audio_path, output_path)
        print(f"Speech saved to {output_path.absolute()}")
        
    engine.shutdown()

if __name__ == "__main__":
    main()
