"""
================================================================================
AI INSTRUCTIONS FOR RUNNING THIS FILE:
================================================================================
This is the unified setup and execution script for the Claire Speech Engine using 
the Fish Speech (8GB VRAM) backend.

If you are an AI assisting the user on a new machine, follow these steps:
1. Ensure the user has created and activated a Python virtual environment.
2. Ensure the Claire Speech Engine is installed (`pip install claire-speech-engine`).
3. Ensure the user has placed a reference audio file named `claire_neutral.wav` 
in the exact same directory as this script.
4. Run this script directly via the terminal: `python interactive_fish.py`

The script is entirely self-healing. Upon running, it will automatically:
- Clone the fish-speech repository if missing.
- Install all heavy dependencies (torchaudio, huggingface_hub, etc.).
- Install fish-speech globally in editable mode (fixes 'tools' ModuleNotFoundError).
- Download the multi-gigabyte checkpoints from HuggingFace.
- Set up the environment paths so CSE can find the backend.
- Drop the user into an interactive prompt to type text and generate WAV files.
================================================================================
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from datetime import datetime

# Configure paths for the local workspace
workspace_dir = Path(__file__).parent.absolute()

# Tell CSE where to look for fish-speech and its models
os.environ["FISH_SPEECH_DIR"] = str(workspace_dir / "fish-speech")
os.environ["FISH_CHECKPOINT_DIR"] = str(workspace_dir / "checkpoints" / "fish-speech-1.5")
os.environ["VOICES_DIR"] = str(workspace_dir)
# Explicitly add fish-speech to the Python path to resolve imports like 'tools'
os.environ["PYTHONPATH"] = os.environ["FISH_SPEECH_DIR"]

def run_cmd(cmd, cwd=None):
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)

def setup_dependencies():
    print("Verifying environment setup...")
    
    # 1. Check for Reference Audio
    neutral_wav = workspace_dir / "claire_neutral.wav"
    if not neutral_wav.exists():
        print(f"⚠️  Missing Reference Audio!")
        print(f"Please put your reference audio in the main folder here: {neutral_wav}")
        print("It MUST be named 'claire_neutral.wav'.")
        print("\nThen run this script again.")
        sys.exit(1)

    # 2. Clone Fish Speech Repository & Install Dependencies
    fish_dir = Path(os.environ["FISH_SPEECH_DIR"])
    if not fish_dir.exists():
        print("\n📥 [1/2] Downloading Fish Speech Repository...")
        run_cmd(["git", "clone", "https://github.com/fishaudio/fish-speech.git", str(fish_dir)])
        
        print("\n📦 Installing core ML dependencies (torchaudio, etc)...")
        # Install basic dependencies ensuring torchaudio is present
        run_cmd([sys.executable, "-m", "pip", "install", "torchaudio", "einops", "omegaconf", "librosa"])
        
        print("\n📦 Registering Fish Speech modules locally...")
        # Installing in editable mode solves all internal path/module errors for Fish Speech
        run_cmd([sys.executable, "-m", "pip", "install", "-e", "."], cwd=str(fish_dir))

    # 3. Download Checkpoints
    ckpt_dir = Path(os.environ["FISH_CHECKPOINT_DIR"])
    vqgan_ckpt = ckpt_dir / "firefly-gan-vq-fsq-8x1024-21hz-generator.pth"
    if not vqgan_ckpt.exists():
        print("\n📥 [2/2] Downloading Fish Speech Checkpoints (Several GBs)...")
        
        try:
            import huggingface_hub
        except ImportError:
            print("Installing huggingface_hub...")
            run_cmd([sys.executable, "-m", "pip", "install", "huggingface_hub"])
            
        print("Starting download from HuggingFace...")
        run_cmd([sys.executable, "-m", "huggingface_hub.commands.huggingface_cli", 
                 "download", "fishaudio/fish-speech-1.5", 
                 "--local-dir", str(ckpt_dir)])
                 
    print("✅ All dependencies are downloaded and ready!")

def main():
    setup_dependencies()
    
    try:
        from cse import SpeechEngine
    except ImportError:
        print("❌ Failed to import cse. Did you install claire-speech-engine?")
        sys.exit(1)

    print("\n🚀 Loading Claire Speech Engine with Fish Speech (8GB VRAM Inference)...")
    
    engine = SpeechEngine()
    
    try:
        # Load the backend (will verify checkpoints exist)
        engine.load_backend("fishspeech")
    except Exception as e:
        print(f"\n❌ Failed to initialize Fish Speech backend:")
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
                
            print("🎙️  Synthesizing... (this may take a moment)")
            result = engine.speak(text)
            
            if result.success:
                # Save the file cleanly to the current directory with a timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                final_path = workspace_dir / f"claire_speech_{timestamp}.wav"
                
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
