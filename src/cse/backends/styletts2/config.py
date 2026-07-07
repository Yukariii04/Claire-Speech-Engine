"""Configuration for StyleTTS2."""
from dataclasses import dataclass
from pathlib import Path

@dataclass
class StyleTTS2Config:
    model_path: Path = Path("models/styletts2")
    output_dir: Path = Path("outputs")
    default_voice: str = "default"
