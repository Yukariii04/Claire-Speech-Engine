# Claire Speech Engine — Example Scripts

Scaffolded by `cse example`. Each script is a standalone demo.

| File | Purpose |
|------|---------|
| example_fishspeech.py | Fish Speech zero-shot cloning demo |
| example_styletts2.py | StyleTTS2 synthesis demo |
| example_kokoro.py | Kokoro multi-voice demo (pass voice id as arg) |

## Usage

```bash
# Run any script directly
python example_kokoro.py
python example_kokoro.py af_bella   # optional: pick a voice

# List all available voices first
cse voices
```

All scripts write `.wav` files into the current directory.
