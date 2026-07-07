"""Configuration for Fish Speech."""
from dataclasses import dataclass
from pathlib import Path

@dataclass
class FishSpeechConfig:
    model_path: Path = Path("models/fishspeech")
    output_dir: Path = Path("outputs")
    default_voice: str = "default"
