"""Fish Speech AcousticBackend — real inference via upstream CLI (PRD-013.6)."""
import os
import subprocess
import uuid as _uuid
from pathlib import Path
from typing import Any

from cse.acoustic.backend.capabilities import BackendCapabilities
from cse.acoustic.backend.interface import AcousticBackend
from cse.backends.kokoro.result import SpeechResult
from cse.backends.kokoro.converter import timeline_to_text
from cse.backends.fishspeech.capabilities import get_fishspeech_capabilities
from cse.backends.fishspeech.exceptions import FishSpeechInitializationError, SpeechGenerationError


# ponytail: defaults match claire_colab.ipynb paths on Colab T4
_DEFAULT_FISH_DIR = "/content/fish-speech"
_DEFAULT_CKPT_DIR = "/content/checkpoints/fish-speech-1.5"
_DEFAULT_VOICES_DIR = "/content/drive/MyDrive/claire/voices"

# ponytail: transcript for the neutral reference audio, reused from claire_colab
_DEFAULT_REF_TRANSCRIPT = (
    "I am currently running my system diagnostics and everything appears to be "
    "functioning within normal parameters. All subsystems are optimal and ready "
    "for your input."
)


class FishSpeechBackend(AcousticBackend):
    def __init__(self, config=None):
        self._initialized = False
        self._voice = None
        # ponytail: env-overridable paths, no config class needed
        self._fish_dir = os.environ.get("FISH_SPEECH_DIR", _DEFAULT_FISH_DIR)
        self._ckpt_dir = os.environ.get("FISH_CHECKPOINT_DIR", _DEFAULT_CKPT_DIR)
        self._voices_dir = os.environ.get("VOICES_DIR", _DEFAULT_VOICES_DIR)
        self._vqgan_ckpt = os.path.join(self._ckpt_dir, "firefly-gan-vq-fsq-8x1024-21hz-generator.pth")

    def initialize(self) -> None:
        # ponytail: just verify the checkpoint exists, no eager GPU load
        if not os.path.exists(self._vqgan_ckpt):
            raise FishSpeechInitializationError(
                f"Fish Speech checkpoint not found at {self._vqgan_ckpt}. "
                f"Run: huggingface-cli download fishaudio/fish-speech-1.5 --local-dir {self._ckpt_dir}"
            )
        self._initialized = True

    def shutdown(self) -> None:
        self._initialized = False
        self._voice = None

    def load_voice(self, voice_name: str) -> str:
        self._voice = voice_name or "neutral"
        return self._voice

    def synthesize(self, timeline: Any) -> SpeechResult:
        if not self._initialized:
            raise SpeechGenerationError("Backend not initialized.")

        text = timeline_to_text(timeline) if hasattr(timeline, "events") else str(timeline)
        if not text.strip():
            raise SpeechGenerationError("No text to synthesize.")

        # ponytail: resolve reference audio, fall back to neutral
        ref_wav = os.path.join(self._voices_dir, f"claire_{self._voice or 'neutral'}.wav")
        if not os.path.exists(ref_wav):
            ref_wav = os.path.join(self._voices_dir, "claire_neutral.wav")
        if not os.path.exists(ref_wav):
            raise SpeechGenerationError(
                f"Reference audio not found. Upload claire_neutral.wav to {self._voices_dir}"
            )

        work_id = _uuid.uuid4().hex[:8]
        stage1_wav = f"/tmp/fish_s1_{work_id}.wav"
        stage1_npy = f"/tmp/fish_s1_{work_id}.npy"
        codes_npy = f"/tmp/fish_codes_{work_id}.npy"
        out_wav = f"/tmp/fish_out_{work_id}.wav"

        try:
            # Stage 1: encode reference audio → VQ tokens
            subprocess.run(
                ["python", "tools/vqgan/inference.py",
                 "-i", ref_wav, "-o", stage1_wav,
                 "--checkpoint-path", self._vqgan_ckpt],
                cwd=self._fish_dir, check=True, capture_output=True, text=True, timeout=60
            )
            if not os.path.exists(stage1_npy):
                raise SpeechGenerationError("VQ encode did not produce token file")

            # Stage 2: text + prompt tokens → semantic codes
            subprocess.run(
                ["python", "tools/llama/generate.py",
                 "--text", text,
                 "--prompt-text", _DEFAULT_REF_TRANSCRIPT,
                 "--prompt-tokens", stage1_npy,
                 "--checkpoint-path", self._ckpt_dir,
                 "--half"],
                cwd=self._fish_dir, check=True, capture_output=True, text=True, timeout=120
            )
            produced = os.path.join(self._fish_dir, "codes_0.npy")
            if not os.path.exists(produced):
                raise SpeechGenerationError("Semantic generation did not produce codes_0.npy")
            os.replace(produced, codes_npy)

            # Stage 3: decode semantic codes → waveform
            subprocess.run(
                ["python", "tools/vqgan/inference.py",
                 "-i", codes_npy, "-o", out_wav,
                 "--checkpoint-path", self._vqgan_ckpt],
                cwd=self._fish_dir, check=True, capture_output=True, text=True, timeout=60
            )

            if not os.path.exists(out_wav):
                raise SpeechGenerationError("Decode did not produce output wav")

            out_path = Path(out_wav)
            file_size = out_path.stat().st_size
            # ponytail: rough duration estimate from file size (PCM 16-bit mono 44100Hz)
            duration = max(0.0, (file_size - 44) / (44100 * 2))

            return SpeechResult(
                success=True,
                audio_path=out_path,
                duration_seconds=duration,
                sample_rate=44100,
                channels=1,
                backend="fishspeech",
                voice=self._voice or "default",
                metadata={"text": text}
            )

        except subprocess.CalledProcessError as e:
            raise SpeechGenerationError(f"Fish Speech inference failed: {e.stderr or e}") from e
        except subprocess.TimeoutExpired as e:
            raise SpeechGenerationError("Fish Speech inference timed out") from e
        finally:
            for f in (stage1_wav, stage1_npy, codes_npy):
                if os.path.exists(f):
                    os.remove(f)

    def validate_timeline(self, timeline: Any) -> None:
        pass

    def get_capabilities(self) -> BackendCapabilities:
        return get_fishspeech_capabilities()

    def list_voices(self) -> list[dict[str, str]]:
        """Discover voices from wav files in the voices directory."""
        # ponytail: voices are just wav files named claire_<voice>.wav
        import glob
        pattern = os.path.join(self._voices_dir, "claire_*.wav")
        voices = []
        for path in sorted(glob.glob(pattern)):
            name = os.path.basename(path).replace("claire_", "").replace(".wav", "")
            voices.append({"id": name, "name": name.title(), "language": "English", "gender": "Unknown"})
        if not voices:
            voices.append({"id": "default", "name": "Default", "language": "English", "gender": "Unknown"})
        return voices

