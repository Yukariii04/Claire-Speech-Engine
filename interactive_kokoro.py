"""
================================================================================
AI INSTRUCTIONS FOR RUNNING THIS FILE:
================================================================================
This is the unified setup and execution script for the Claire Speech Engine using 
the Kokoro (CPU/ONNX) backend.

If you are an AI assisting the user on a new machine, follow these steps:
1. Ensure the user has created and activated a Python virtual environment.
2. Ensure the Claire Speech Engine is installed (`pip install claire-speech-engine`).
3. Run this script directly via the terminal: `python interactive_kokoro.py`

The script is entirely self-healing. Upon running, it will automatically:
- Create the 'models/kokoro' directory structure.
- Download the ONNX models directly from GitHub releases if missing.
- Install the required dependencies (`kokoro-onnx`, `soundfile`).
- Drop the user into an interactive prompt to type text and generate WAV files.
================================================================================
"""

import os
import sys
import subprocess
import shutil
import urllib.request
from pathlib import Path
from datetime import datetime

# Configure paths
workspace_dir = Path(__file__).parent.absolute()
kokoro_models_dir = workspace_dir / "models" / "kokoro"

# Files to download
ONNX_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx"
VOICES_URL = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"

def run_cmd(cmd):
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)

def download_file(url, dest_path):
    if not dest_path.exists():
        print(f"📥 Downloading {dest_path.name} from {url}...")
        try:
            urllib.request.urlretrieve(url, dest_path)
            print(f"✅ Downloaded {dest_path.name}")
        except Exception as e:
            print(f"❌ Failed to download {url}: {e}")
            sys.exit(1)

def setup_dependencies():
    print("Verifying Kokoro environment setup...")
    
    # 1. Install dependencies
    try:
        import kokoro_onnx
        import soundfile
    except ImportError:
        print("\n📦 Installing Kokoro backend dependencies (kokoro-onnx, soundfile)...")
        run_cmd([sys.executable, "-m", "pip", "install", "kokoro-onnx", "soundfile"])

    # 2. Download Models
    kokoro_models_dir.mkdir(parents=True, exist_ok=True)
    
    onnx_path = kokoro_models_dir / "kokoro-v1.0.onnx"
    voices_path = kokoro_models_dir / "voices-v1.0.bin"
    
    download_file(ONNX_URL, onnx_path)
    download_file(VOICES_URL, voices_path)
                 
    print("✅ All Kokoro dependencies are downloaded and ready!")

def main():
    setup_dependencies()
    
    try:
        from cse import SpeechEngine
    except ImportError:
        print("❌ Failed to import cse. Did you install claire-speech-engine?")
        sys.exit(1)

    print("\n🚀 Loading Claire Speech Engine with Kokoro (ONNX/CPU)...")
    
    os.chdir(workspace_dir)
    engine = SpeechEngine()
    
    try:
        engine.load_backend("kokoro")
    except Exception as e:
        print(f"\n❌ Failed to initialize Kokoro backend:")
        print(e)
        sys.exit(1)
        
    # Calling load_voice() with no arguments tells the engine to use the user's
    # saved CLI preference (if set), otherwise falling back to the backend default
    engine.load_voice()
    
    from cse.config.user_config import get_preference
    voice_name = get_preference("voice") or engine._runtime.get_backend().list_voices()[0]["id"]
    print(f"\n✅ Engine Ready! (Using voice: {voice_name})")
    
    while True:
        try:
            text = input("\n📝 Enter text to synthesize (or Ctrl+C to exit): ")
            if not text.strip():
                continue
                
            print("🎙️  Synthesizing... (Super fast on CPU!)")
            result = engine.speak(text)
            
            if result.success:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                final_path = workspace_dir / f"kokoro_speech_{timestamp}.wav"
                
                shutil.copy2(result.audio_path, final_path)
                print(f"✅ Success! Audio saved to: {final_path}")
            else:
                print(f"❌ Synthesis failed.")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error during synthesis: {e}")

if __name__ == "__main__":
    main()
