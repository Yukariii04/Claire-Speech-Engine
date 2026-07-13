"""Evaluation tool for comparing acoustic backends (PRD-013).

Usage:
  python evaluation/compare.py
"""

from pathlib import Path
from typing import Any

from cse import SpeechEngine

ROOT = Path(__file__).resolve().parents[1]
PROMPTS_FILE = ROOT / "evaluation" / "prompts" / "standard.txt"
OUTPUT_DIR = ROOT / "evaluation" / "outputs"


def load_prompts() -> list[str]:
    if not PROMPTS_FILE.exists():
        return ["Hello world."]
    return [line.strip() for line in PROMPTS_FILE.read_text().splitlines() if line.strip()]


def print_capabilities(backend: str, caps: dict[str, Any]) -> None:
    print(f"\n--- {backend.upper()} CAPABILITIES ---")
    for k, v in caps.items():
        print(f"  {k}: {v}")


def evaluate_backend(engine: SpeechEngine, backend: str, prompts: list[str]) -> None:
    print(f"\nEvaluating Backend: {backend}")
    try:
        engine.load_backend(backend)
    except Exception as e:
        print(f"  Skipped (failed to load backend: {e})")
        return

    print_capabilities(backend, engine.get_backend_capabilities())

    try:
        from cse.voice import register_voice_package, VoicePackage, VoiceMetadata
        from pathlib import Path
        meta = VoiceMetadata(id="dummy", name="Dummy", version="1.0.0", author="CSE", language="en", backend="dummy", sample_rate=24000, channels=1, description="Test", license="MIT")
        pkg = VoicePackage(metadata=meta, path=Path("."))
        register_voice_package(pkg)
    except Exception:
        pass

    try:
        if backend == "kokoro":
            engine.load_voice("dummy") # Kokoro uses its own voice internally for now in compare or will fall back
        else:
            engine.load_voice("dummy")
    except Exception as e:
        print(f"  Skipped (failed to load voice: {e})")
        return

    backend_out_dir = OUTPUT_DIR / backend
    backend_out_dir.mkdir(parents=True, exist_ok=True)

    for i, text in enumerate(prompts):
        try:
            result = engine.speak(text)
            if result.success and result.audio_path:
                print(f"  [{i+1}/{len(prompts)}] SUCCESS: {text[:20]}... -> {result.audio_path.name}")
            else:
                print(f"  [{i+1}/{len(prompts)}] PROCESSED (no audio): {text[:20]}...")
        except Exception as e:
            if backend == "dummy" and "does not synthesize" in str(e):
                print(f"  [{i+1}/{len(prompts)}] Dummy correctly rejected synthesis.")
            else:
                print(f"  [{i+1}/{len(prompts)}] ERROR: {e}")


def main() -> None:
    prompts = load_prompts()
    print(f"Loaded {len(prompts)} evaluation prompts.")
    
    engine = SpeechEngine()
    
    for backend in ["dummy", "kokoro", "styletts2"]:
        evaluate_backend(engine, backend, prompts)

    engine.shutdown()
    print("\nEvaluation complete.")


if __name__ == "__main__":
    main()
