"""Test script to validate both Kokoro and StyleTTS2 backends.

This script demonstrates how to switch backends and synthesize audio
using the new integrated reasoning pipeline.

INSTRUCTIONS FOR TESTING THE .WHL:
1. Install the wheel in your new environment: `pip install claire_speech_engine-1.0.4-py3-none-any.whl`
2. Copy this script and your `models` folder into a new test directory.
3. Your directory structure should look like this:
   /test_folder
   ├── test_both_backends.py
   └── models/
       ├── kokoro/
       │   ├── kokoro-v1.0.onnx
       │   └── voices-v1.0.bin
       └── styletts2/
           └── ... (styletts2 models)
4. Run: `python test_both_backends.py`
"""

import sys
from pathlib import Path
from cse.api.engine import SpeechEngine

def setup_backend_config(engine: SpeechEngine, backend_id: str, model_dir: Path) -> None:
    """Helper to inject explicit model paths since the public API doesn't accept config directly yet."""
    backend = engine._runtime.get_backend()
    
    if backend_id == "kokoro":
        from cse.backends.kokoro.config import KokoroConfig
        backend._config = KokoroConfig(
            model_path=model_dir / "kokoro" / "kokoro-v1.0.onnx",
            voices_path=model_dir / "kokoro" / "voices-v1.0.bin",
            output_dir="."
        )
    elif backend_id == "styletts2":
        from cse.backends.styletts2.config import StyleTTS2Config
        backend._config = StyleTTS2Config(
            model_dir=model_dir / "styletts2",
            output_dir="."
        )
        
    # Re-initialize the backend with the new configuration
    backend.shutdown()
    backend.initialize()

def test_kokoro(engine: SpeechEngine, model_dir: Path):
    print("\n--- Testing Kokoro Backend ---")
    try:
        engine.load_backend("kokoro")
        setup_backend_config(engine, "kokoro", model_dir)
        engine.load_voice("af_heart")
        
        result = engine.speak("Hello from Kokoro! The Performance Graph integration works flawlessly.")
        print(f"Success! Audio saved to: {result.audio_path}")
        print(f"Graph Output: {result.metadata.get('text', '')}")
    except Exception as e:
        print(f"Kokoro failed: {e}")

def test_styletts2(engine: SpeechEngine, model_dir: Path):
    print("\n--- Testing StyleTTS2 Backend ---")
    try:
        engine.load_backend("styletts2")
        setup_backend_config(engine, "styletts2", model_dir)
        engine.load_voice("claire_neutral")
        
        result = engine.speak("Hello from StyleTTS2! The Performance Graph integration works flawlessly.")
        print(f"Success! Audio saved to: {result.audio_path}")
        print(f"Graph Output: {result.metadata.get('text', '')}")
    except Exception as e:
        print(f"StyleTTS2 failed: {e}")

if __name__ == "__main__":
    # Expect models in the current working directory
    model_dir = Path("models").absolute()
    
    if not model_dir.exists():
        print(f"CRITICAL ERROR: Models directory not found at {model_dir}")
        print("Please ensure you have copied the 'models' folder into your current directory.")
        sys.exit(1)
        
    print(f"Using models from: {model_dir}")
    
    engine = SpeechEngine()
    
    test_kokoro(engine, model_dir)
    test_styletts2(engine, model_dir)
    
    engine.shutdown()
