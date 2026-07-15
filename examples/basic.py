"""Basic usage of the Claire Speech Engine."""

import sys
from pathlib import Path
from cse import SpeechEngine

def main():
    model_dir = Path("models").absolute()
    if not model_dir.exists():
        print(f"CRITICAL ERROR: Models directory not found at {model_dir}")
        sys.exit(1)
        
    engine = SpeechEngine()
    engine.load_backend("kokoro")
    
    # Inject config for wheel users
    backend = engine._runtime.get_backend()
    from cse.backends.kokoro.config import KokoroConfig
    backend._config = KokoroConfig(
        model_path=model_dir / "kokoro" / "kokoro-v1.0.onnx",
        voices_path=model_dir / "kokoro" / "voices-v1.0.bin",
    )
    backend.shutdown()
    backend.initialize()

    engine.load_voice("af_heart")
    
    result = engine.speak("Welcome to the Claire Speech Engine.")
    
    if result.success:
        print(f"Success! Audio saved to: {result.audio_path}")
    else:
        print("Failed to generate speech")
        
    engine.shutdown()

if __name__ == "__main__":
    main()
